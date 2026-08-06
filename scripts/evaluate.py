"""Two-tier evaluation: Tier 1 (free, local retrieval only) checks every
question; Tier 2 (costs Gemini calls) only re-runs Tier 1's failures through
the full retrieve->rerank->answer pipeline, to conserve API quota."""
from src.embedder import embed_query
from src.vector_store import search, close_client
from src.graph import build_graph

# (question, expected_pdf, expected_page, expected_substring_in_answer)
GROUND_TRUTH = [
    ("What was the Q1 revenue?", "sales_report.pdf", 1, "120"),
    ("What was the Q4 revenue?", "sales_report.pdf", 1, "180"),
    ("Which region had the highest growth percent?", "sales_report.pdf", 2, "South"),
    ("What was the East region's revenue?", "sales_report.pdf", 2, "150"),
    ("What is HEICO's stock ticker symbol and what state is it incorporated in?", "messy_sample.pdf", 3, "Florida"),
    ("How many shares of Class A Common Stock are outstanding?", "messy_sample.pdf", 4, "84,213,758"),
    ("What fiscal year end date is this 10-K for?", "messy_sample.pdf", 5, "October 31, 2025"),
    ("In what year was HEICO Corporation originally organized?", "messy_sample.pdf", 6, "1957"),
    ("What percentage of net sales did the Flight Support Group account for in fiscal 2025?", "messy_sample.pdf", 6, "70"),
    ("Approximately how many acquisitions has HEICO completed since 1990?", "messy_sample.pdf", 8, "107"),
    ("What is the Q2 2026 real GDP growth projection?", "fed_sample.pdf", 5, "1.5"),
    ("What was the Q1 2026 change in Personal Consumption Expenditures?", "fed_sample.pdf", 4, "0.5"),
    ("What is the 10-year annual GDP growth rate as of Q2 2026?", "fed_sample.pdf", 6, "2.4"),
    ("What was the year-over-year retail sales percent change in June?", "fed_sample.pdf", 7, "6.7"),
    ("What was the June year-over-year change in real disposable personal income?", "fed_sample.pdf", 8, "2.5"),
]


def run_tier1():
    """Raw retrieval accuracy check. No Gemini calls -- local model only."""
    results = []
    for question, expected_pdf, expected_page, _ in GROUND_TRUTH:
        vec = embed_query(question)
        hits = search(vec, top_k=3)
        found = any(h["pdf"] == expected_pdf and h["page_number"] == expected_page for h in hits)
        results.append((question, expected_pdf, expected_page, found))
    return results


def run_tier2(failures):
    """Full pipeline (retrieve -> rerank -> answer) on Tier 1 failures only."""
    graph = build_graph()
    results = []
    for question, expected_pdf, expected_page, expected_substring in failures:
        result = graph.invoke({"question": question})
        pages = [(r["pdf"], r["page_number"]) for r in result["retrieved"]]
        page_found = (expected_pdf, expected_page) in pages
        answer_correct = expected_substring in result["answer"]
        results.append((question, page_found, answer_correct, result["answer"]))
    return results


def main():
    print("=== TIER 1: Raw retrieval accuracy (free, local only) ===\n")
    tier1_results = run_tier1()
    tier1_pass = sum(1 for *_, found in tier1_results if found)
    for question, expected_pdf, expected_page, found in tier1_results:
        status = "PASS" if found else "FAIL"
        print(f"[{status}] {question}")
        if not found:
            print(f"       expected {expected_pdf} page {expected_page}")
    print(f"\nTier 1: {tier1_pass}/{len(tier1_results)} correct ({100 * tier1_pass / len(tier1_results):.0f}%)\n")

    failures = [
        gt for (q, epdf, epage, found), gt in zip(tier1_results, GROUND_TRUTH) if not found
    ]

    if failures:
        print(f"=== TIER 2: Full pipeline (rerank + answer) on {len(failures)} Tier 1 failure(s) ===\n")
        tier2_results = run_tier2(failures)
        tier2_pass = sum(1 for _, _, correct, _ in tier2_results if correct)
        for question, page_found, answer_correct, answer in tier2_results:
            status = "RECOVERED" if answer_correct else "STILL FAILING"
            print(f"[{status}] {question}")
            print(f"       page found: {page_found}, answer: {answer[:100]}")
        print(f"\nTier 2 recovery: {tier2_pass}/{len(failures)} of Tier 1's failures fixed by reranking")

        total_correct = tier1_pass + tier2_pass
        print(f"\n=== OVERALL: {total_correct}/{len(GROUND_TRUTH)} correct ({100 * total_correct / len(GROUND_TRUTH):.0f}%) with reranking enabled ===")
    else:
        print("All Tier 1 questions passed -- no reranking needed for this question set.")

    close_client()


if __name__ == "__main__":
    main()
