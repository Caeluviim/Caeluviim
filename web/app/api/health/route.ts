import { CATEGORY_KEYS, PROTOCOL_VERSION } from "../../../lib/protocol";
import { hasDatabaseBinding } from "../../../lib/store";
import { env } from "cloudflare:workers";

export function GET() {
  return Response.json({
    ok: true,
    service: "caeluviim-protocol",
    protocolVersion: PROTOCOL_VERSION,
    categoryCount: CATEGORY_KEYS.length,
    dapValidatorSigning: Boolean(
      env.DAP_VALIDATOR_ID &&
      env.DAP_VALIDATOR_KEY_ID &&
      env.DAP_VALIDATOR_PUBLIC_KEY &&
      env.DAP_VALIDATOR_PRIVATE_KEY_PKCS8,
    ),
    invariants: {
      everyCategoryVisible: true,
      dynamicColumnOrder: true,
      provenanceInRow: true,
      csvExport: true,
      graphProjection: true,
      sourceBoundKnowledgeRecords: true,
      evidenceBoundKnowledgeEdges: true,
      explicitTopicCoverageGaps: true,
      remoteMcpEndpoint: true,
      groundedStatementRejection: true,
      appendOnlyEventEnvelope: true,
      contentAddressedDeduplication: true,
      districtOperationsAreContentAddressed: true,
      districtRulesetsAreVersionBound: true,
      districtTimeIsCheckpointDerived: true,
      signedDistrictGenesis: true,
      stagedDistrictValidation: true,
      deterministicDistrictReconstruction: true,
      acceptedHistorySeparatedFromProjection: true,
      ballotBoundProposalDecisions: true,
      causallySafeNonDestructiveReversal: true,
      districtMcpTools: true,
      districtAwareNaturalLanguageResponse: true,
      signedValidationDispositions: true,
      languageExpressionContentAndForceSeparated: true,
      evidenceBoundOperativeEffects: true,
      effectiveNormativeForceRequiresAuthority: true,
      claimedAndEffectiveForceRemainDistinct: true,
      languageGraphJsonLdAndNQuadsExport: true,
    },
    storage: hasDatabaseBinding() ? "d1" : "stateless-fallback",
  });
}
