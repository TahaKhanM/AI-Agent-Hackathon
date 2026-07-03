"""Conformance bench — reports in BasedAI's own published evaluation vocabulary.

See Idea/refinement/02-architecture-refinement.md §2.7. conformance_bench generates the
sponsor's exact protocol topology (5 levels / 20 roles / 1,000 ACL-tagged docs) + 10,000
ground-truth queries (>=3,000 deny-expected so FNR<0.1% is claimable), and reports
FNR/FPR/P50/P99/overhead/drift/TTC vs each published threshold to RESULTS.md.

Owner: T3 (decoupled from product code — zero imports from the compiler under test; the
independent oracle produces the ground-truth labels). See Plan/BUILD-PLAN.md §3.1.
"""
