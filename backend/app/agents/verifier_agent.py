from app.agents.state import AgentState


class EvidenceVerifier:
    """
    Agent responsible for checking whether retrieved repository
    evidence is sufficient, relevant, and current.
    """

    PLANNED_MARKERS = {
        "future work",
        "future stage",
        "next stage",
        "planned architecture",
        "planned",
        "will include",
        "will be introduced",
        "next version",
        "research direction",
        "coming soon",
    }

    def verify(self, state: AgentState) -> AgentState:
        question_type = state.get("question_type", "general")
        retrieved_chunks = state.get("retrieved_chunks", [])

        evidence_count = len(retrieved_chunks)

        if not retrieved_chunks:
            return {
                **state,
                "verification_status": "insufficient",
                "evidence_summary": "No repository evidence was retrieved.",
            }

        unique_files = set()
        implemented_evidence = []
        planned_evidence = []
        distances = []

        for chunk in retrieved_chunks:
            file_path = chunk.get("file_path", "")
            if file_path:
                unique_files.add(file_path)

            distance = chunk.get("distance")
            if isinstance(distance, (int, float)):
                distances.append(distance)

            content = chunk.get("content", "").lower()
            is_planned = any(marker in content for marker in self.PLANNED_MARKERS)

            if is_planned:
                planned_evidence.append(chunk)
            else:
                implemented_evidence.append(chunk)

        unique_file_count = len(unique_files)
        average_distance = sum(distances) / len(distances) if distances else None

        # Minimum evidence requirements
        if question_type == "architecture":
            minimum_evidence, minimum_files = 5, 3
        elif question_type == "repository_overview":
            minimum_evidence, minimum_files = 4, 2
        elif question_type in {"technology", "code_question"}:
            minimum_evidence, minimum_files = 2, 1
        else:
            minimum_evidence, minimum_files = 2, 1

        evidence_sufficient = (
            evidence_count >= minimum_evidence and unique_file_count >= minimum_files
        )

        distance_text = f"{average_distance:.3f}" if average_distance is not None else "unavailable"
        implementation_status = (
            "implemented_evidence_available" if implemented_evidence else "planned_only"
        )

        evidence_summary = (
            f"Retrieved {evidence_count} evidence chunks "
            f"from {unique_file_count} unique files. "
            f"Average retrieval distance: {distance_text}. "
            f"Implemented/current evidence: {len(implemented_evidence)} chunks. "
            f"Planned/future evidence: {len(planned_evidence)} chunks. "
            f"Required at least {minimum_evidence} chunks "
            f"from {minimum_files} unique file(s)."
        )

        verification_status = "sufficient" if evidence_sufficient else "insufficient"

        print(f"[EvidenceVerifier] Status: {verification_status}")
        print(f"[EvidenceVerifier] Evidence chunks: {evidence_count}")
        print(f"[EvidenceVerifier] Unique files: {unique_file_count}")
        print(f"[EvidenceVerifier] Implemented evidence: {len(implemented_evidence)}")
        print(f"[EvidenceVerifier] Planned evidence: {len(planned_evidence)}")
        print(f"[EvidenceVerifier] Average distance: {distance_text}")
        print(f"[EvidenceVerifier] {evidence_summary}")

        # Filtering planned evidence for architecture/overview questions
        filtered_chunks = retrieved_chunks
        if question_type in {"architecture", "repository_overview"}:
            if implemented_evidence:
                filtered_chunks = implemented_evidence
                print(
                    "[EvidenceVerifier] Filtered planned evidence. "
                    f"Answer generation will use {len(filtered_chunks)} current chunks."
                )

        return {
            **state,
            "retrieved_chunks": filtered_chunks,
            "verification_status": verification_status,
            "evidence_summary": evidence_summary,
        }


evidence_verifier = EvidenceVerifier()


def evidence_verifier_node(state: AgentState) -> AgentState:
    """
    LangGraph node wrapper for Evidence Verifier.
    """
    return evidence_verifier.verify(state)
