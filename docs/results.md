# Results narrative

All 720 planned API requests completed. Llama 3.1 8B achieved the highest overall task success (70.0%) and the lowest attack-success rate (9.3%). GPT-OSS 20B achieved the strongest refusal correctness (80.7%) but had low benign task success (35.0%), largely associated with strict-output nonconformance and indirect-injection failures. Nemotron Mini 4B achieved 99.2% JSON conformance and 80.0% benign task success, yet recorded the highest attack-success rate (38.0%).

The central finding is a professionalism-safety mismatch. Structured conformance and benign utility did not guarantee safe authority handling. In paired adversarial comparisons, Llama's attack-success rate was lower than Nemotron's after Holm correction (adjusted p < 0.001), and GPT-OSS also had a lower rate than Nemotron (adjusted p = 0.001).

The benchmark observed zero planted-canary disclosures. This does not erase other failures: some agents generated queries for forbidden columns, accepted unverified authority claims, followed injected instructions, or hallucinated nonexistent schema elements.
