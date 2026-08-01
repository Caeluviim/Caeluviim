# Interlocutor Operation → Graph Crosswalk

**Status:** Proposed v0.1.0  
**Coverage:** Canonical operation concepts derived from the supplied Tables 1–19. Repeated table rows are represented as occurrences of one canonical concept unless a documented theoretical distinction requires separate concepts.

## 1. Canonicalization rule

| Source condition | Graph treatment |
|---|---|
| Same operation name and materially equivalent definition in multiple tables | One `CanonicalOperation` node; each table row becomes an `OperationDefinitionOccurrence` linked by `definesOperation`. |
| Same label but materially distinct theoretical account | Separate `CanonicalOperation` nodes linked by `contrastsWith`, `extends`, or `revisesConcept`. |
| Different labels that describe the same operation | One canonical node plus `hasAlias` edges. |
| Broad theory containing several executable operations | Theory is a `Theory` node; executable operations are separate `CanonicalOperation` nodes linked by `specifiedByTheory`. |
| Citation correction | Original occurrence is retained; corrected occurrence is linked by `prov:wasRevisionOf` and a `CorrectionEvent`. |

## 2. Core crosswalk

| Canonical ID | Operation / aliases | Source table(s) | Graph realization | Domain → Range | Inference status |
|---|---|---:|---|---|---|
| `io:semiosis` | Sign relation; semiosis; triadic sign relation | 1, 11 | `SignRelation` node with `hasSignVehicle`, `hasObject`, `hasInterpretant` | SignVehicle × Object × Interpretant | analytic |
| `io:linguistic-sign` | Signifier/signified | 1, 11 | `LinguisticSign` node | Signifier → Signified | analytic |
| `io:sign-arbitrariness` | Arbitrariness of the sign | 1, 11 | `ConventionRelation` | Form → MeaningConvention | theoretical |
| `io:iconicity` | Icon | 1, 11 | `representsByResemblance` | Sign → Object | inferred |
| `io:indexical-sign` | Index | 1, 11 | `representsByConnection` | Sign → Object | inferred |
| `io:symbolic-sign` | Symbol | 1, 11 | `representsByConvention` | Sign → Object | inferred |
| `io:value-through-difference` | Linguistic value; systemic contrast | 1, 6, 11, 16 | `contrastsWith` plus `SystemValueAssignment` | LinguisticUnit ↔ LinguisticUnit | analytic |
| `io:interpretant` | Interpretant operation | 1, 11 | `Interpretation` / `hasInterpretant` | SignRelation → Interpretation | inferred, contestable |
| `io:code-membership` | Code; cultural code | 11 | `usesCode` / `belongsToCode` | Sign → Code | inferred |
| `io:cultural-semiosis` | Cultural semiotics | 11, 14 | `CulturalInterpretation` | Sign × CulturalContext → Interpretation | inferred, contestable |
| `io:sense-reference` | Sense/reference distinction | 2, 13 | `ReferenceAssignment` with `hasSense` and `hasReferent` | Expression → Referent | inferred, contestable |
| `io:compositionality` | Compositional meaning; principle of compositionality | 2, 3 | `CompositionDerivation` | ExpressionParts × CompositionRule → Meaning | analytic/inferred |
| `io:denotation` | Denoting expression | 2, 13 | `denotes` | Expression → Entity/Set | inferred |
| `io:definite-description` | Theory/analysis of descriptions | 2, 13 | `DescriptionAnalysis` | Description → QuantificationalStructure | inferred, contestable |
| `io:rigid-designation` | Naming as direct reference; proper names and rigid designation | 2, 13 | `rigidlyDesignates` | Name → Entity | theoretical/inferred |
| `io:referential-use` | Referential description | 2 | `DescriptionUse` with mode `referential` | DescriptionOccurrence → IntendedEntity | inferred, contestable |
| `io:attributive-use` | Attributive description | 2 | `DescriptionUse` with mode `attributive` | DescriptionOccurrence → SatisfierRole | inferred, contestable |
| `io:externalist-dependence` | Meaning externalism | 2 | `dependsOnExternalFactor` | LexicalMeaning → Environment/SocialPractice | theoretical |
| `io:character-content` | Character/content of indexicals | 2, 4 | `ContextualContentAssignment` | Indexical × Context → Content | analytic/inferred |
| `io:predication` | Predicate attribution | 3 | `PredicateApplication` | Predicate × Argument(s) → Proposition | analytic |
| `io:declarative-statement` | Statement and truth/falsity distinction | 3 | `hasSentenceMood` + `expressesProposition` | Utterance → Proposition | analytic/inferred |
| `io:thought-content` | Objective conceptual content | 3 | `expressesThought` | Expression → ThoughtContent | theoretical/inferred |
| `io:truth-value-bearing` | Truth-value bearer | 3 | `isTruthAssessable` | Proposition → BooleanCapability | analytic |
| `io:truth-condition` | Semantic conception; truth-condition meaning | 3 | `TruthConditionSet` | Proposition → WorldCondition | analytic/inferred |
| `io:formal-semantic-composition` | Montague-style composition | 3 | `SemanticDerivation` | SyntaxTree × InterpretationFunction → Denotation | analytic |
| `io:assertion` | Assertion as illocutionary act/commitment/social practice | 3, 7 | `ForceAssignment(assertive)` and `CommitmentEvent` | Utterance × Context → Commitment | inferred, contestable |
| `io:deictic-field` | Deictic field; pointing function | 4 | `DeicticContext` | UtteranceEvent → ContextCoordinates | analytic |
| `io:deictic-origo` | Deictic center | 4 | `hasOrigo` | Context → Speaker × Place × Time | analytic |
| `io:indexical-expression` | Indexical | 4, 13 | `IndexicalResolution` | Expression × Context → Referent/Content | inferred |
| `io:person-deixis` | First/second person deixis | 4 | `resolvesParticipantRole` | Pronoun × Context → Agent | inferred |
| `io:place-deixis` | Spatial deixis | 4 | `resolvesLocation` | DeicticExpression × Context → Place | inferred |
| `io:time-deixis` | Temporal deixis | 4 | `resolvesTime` | DeicticExpression × Context → TimeInterval | inferred |
| `io:social-deixis` | Honorific/social-role deixis | 4, 14 | `indexesSocialRelation` | Expression × Context → SocialRelation | inferred, contestable |
| `io:essential-indexical` | Essential first-person indexical | 4 | `requiresPerspective` | Proposition → Perspective | theoretical/inferred |
| `io:metaphorical-transfer` | Metaphor as transfer | 5, 9 | `MetaphorMapping` | SourceDomain → TargetDomain | inferred, contestable |
| `io:metaphor-interaction` | Interaction theory; tenor/vehicle | 5 | `MetaphorInteraction` with `hasTenor`, `hasVehicle` | ConceptSystem × ConceptSystem → EmergentMeaning | inferred |
| `io:conceptual-metaphor` | Conceptual metaphor; conceptual mapping | 5, 12, 18 | `ConceptualMapping` | SourceDomain → TargetDomain | inferred, contestable |
| `io:prototype-category` | Prototype categorization/theory | 5, 12, 18 | `PrototypeAssignment` | Category → PrototypeMember | empirical/inferred |
| `io:basic-level-category` | Basic-level category | 5, 12 | `hasBasicLevel` | Taxonomy → Category | empirical/inferred |
| `io:family-resemblance` | Family resemblance structure | 12, 18 | `FamilyResemblanceCluster` | Category → FeatureOverlapGraph | inferred |
| `io:radial-category` | Radial category | 18 | `RadialCategoryStructure` | Category → CentralAndExtendedSenses | inferred |
| `io:frame-evocation` | Frame semantics; semantic frame | 5, 12, 18 | `evokesFrame` | LexicalItem/Utterance → Frame | inferred, contestable |
| `io:construal` | Construal operation | 5, 12, 18 | `ConstrualAssignment` | Scene × Perspective → Presentation | inferred, contestable |
| `io:profiling` | Profiling/base; attention direction | 5, 12, 18 | `profiles` | Expression → ConceptualSubstructure | inferred |
| `io:figure-ground` | Figure-ground organization | 12, 18 | `FigureGroundAssignment` | Scene → Figure × Ground | inferred |
| `io:image-schema` | Image schema | 12, 18 | `instantiatesImageSchema` | Expression/Concept → ImageSchema | inferred |
| `io:embodiment` | Embodied cognition | 12, 18 | `groundedInEmbodiedPattern` | Concept → SensorimotorPattern | theoretical/inferred |
| `io:mental-space` | Mental spaces | 12, 18 | `MentalSpace` node and `projectsIntoSpace` | DiscourseElement → MentalSpace | inferred |
| `io:conceptual-blending` | Conceptual blending/integration network | 5, 12, 18 | `BlendNetwork` with input/generic/blended spaces | MentalSpaceSet → BlendedSpace | inferred, contestable |
| `io:frame-shift` | Frame shifting | 18 | `FrameShiftEvent` | PriorFrame × NewContext → NewFrame | inferred |
| `io:syntagmatic-relation` | Ordered combination | 6 | `precedesInConstruction` / `combinesWith` | LinguisticUnit ↔ LinguisticUnit | analytic |
| `io:distributional-analysis` | Distributional analysis/learning | 6, 17 | `DistributionProfile` | LinguisticUnit → ContextDistribution | analytic/empirical |
| `io:constituency` | Constituency | 6, 16 | `containsConstituent` | SyntacticNode → SyntacticNode | analytic/inferred |
| `io:phrase-structure` | Phrase-structure grammar | 6, 16 | `PhraseStructureDerivation` | GrammarRule × Constituents → Phrase | analytic |
| `io:syntactic-transformation` | Transformational operation | 6, 16 | `SyntacticTransformationEvent` | SyntaxRepresentation → SyntaxRepresentation | analytic |
| `io:deep-surface-relation` | Deep/surface structure | 6, 16 | `realizesUnderlyingStructure` | SurfaceForm → UnderlyingStructure | theory-relative |
| `io:xbar-projection` | X-bar theory | 6 | `projectsHead` | Head → Intermediate/MaximalProjection | theory-relative |
| `io:dependency` | Dependency/head-dependent relation | 6, 16 | `dependsOnHead` | Dependent → Head | analytic/inferred |
| `io:constituency-test` | Substitution/movement/coordination test | 6 | `ConstituencyTestEvent` | Span → TestResult | analytic |
| `io:morpheme-segmentation` | Morpheme as minimal unit | 6, 16 | `hasMorpheme` | Word → Morpheme | analytic/inferred |
| `io:inflection` | Morphological inflection | 6, 16 | `InflectionEvent` | Lexeme × FeatureBundle → WordForm | analytic |
| `io:derivation` | Derivational morphology | 6, 16 | `DerivationEvent` | Lexeme × DerivationalRule → Lexeme | analytic |
| `io:morphological-productivity` | Productive word formation | 16 | `ProductiveRuleApplication` | MorphologicalRule × Base → NovelForm | inferred |
| `io:phonemic-contrast` | Phoneme | 16 | `contrastsPhonemicallyWith` | Phoneme ↔ Phoneme | analytic |
| `io:distinctive-feature` | Distinctive features | 16 | `hasPhonologicalFeature` | Segment → Feature | analytic |
| `io:phonological-rule` | Phonological operation | 16 | `PhonologicalTransformationEvent` | UnderlyingForm → SurfaceForm | analytic |
| `io:feature-agreement` | Feature-based syntax | 16 | `agreesWith` | SyntacticElement ↔ SyntacticElement | analytic |
| `io:constraint-ranking` | Optimality Theory | 16 | `ConstraintEvaluation` | Candidate × RankedConstraintSet → OptimalityResult | theory-relative |
| `io:linguistic-recursion` | Recursive embedding | 16 | `recursivelyContains` | SyntacticStructure → SyntacticStructure | analytic |
| `io:language-as-action` | Performative language | 7, 14 | `SpeechActEvent` | Utterance × Context → SocialAction | inferred, contestable |
| `io:locutionary-act` | Locution | 7 | `LocutionEvent` | Speaker → MeaningfulExpression | analytic |
| `io:illocutionary-act` | Illocution | 7 | `ForceAssignment` | Utterance × Context → IllocutionType | inferred, contestable |
| `io:perlocutionary-effect` | Perlocution | 7 | `PerlocutionEffectAssertion` | UtteranceEvent → AudienceEffect | evidential/inferred |
| `io:felicity-condition` | Felicity conditions | 7 | `FelicityAssessment` | SpeechAct × InstitutionalContext → Status | inferred |
| `io:directive` | Request/command | 7 | `ForceAssignment(directive)` | Utterance → RequestedAction | inferred, contestable |
| `io:commissive` | Promise/commitment | 7 | `ForceAssignment(commissive)` + `CommitmentEvent` | Utterance → FutureActionCommitment | inferred, contestable |
| `io:expressive` | Apology, thanks, congratulations | 7 | `ForceAssignment(expressive)` | Utterance → ExpressedAttitude | inferred, contestable |
| `io:declaration` | Institutionally effective declaration | 7, 14 | `DeclarationEvent` | AuthorizedUtterance × Institution → InstitutionalStateChange | inferred plus authority validation |
| `io:communicative-intention` | Gricean intention | 7 | `IntentionAssignment` | Agent × Utterance → IntendedMeaning | inferred, contestable |
| `io:cooperative-principle` | Gricean cooperation/maxims | 7 | `CooperationAssessment` | Turn × ConversationContext → MaximStatus | inferred, contestable |
| `io:conversational-implicature` | Implicature | 7, 13 | `implicates` via `ImplicatureAssertion` node | Interpretation → Proposition | inferred, defeasible, contestable |
| `io:conversation-order` | Conversation as organized system | 8, 15 | `ConversationStructure` | TurnSet → SequentialOrganization | analytic/inferred |
| `io:turn-taking` | Turn-taking system | 8, 15 | `TurnAllocationEvent` | ConversationState → SpeakerTurn | analytic/inferred |
| `io:transition-relevance-place` | TRP | 8, 15 | `TransitionOpportunity` | TurnConstructionUnit → TimePoint | inferred |
| `io:turn-construction-unit` | TCU | 15 | `TurnConstructionUnit` | Turn → LinguisticSpan | analytic/inferred |
| `io:adjacency-pair` | Adjacency pair | 8, 15 | `AdjacencyPair` node with first/second pair parts | Turn → Turn | analytic/inferred |
| `io:conditional-relevance` | First/second pair relevance | 15 | `makesConditionallyRelevant` | FirstPairPart → ExpectedSecondPairType | inferred |
| `io:sequence-organization` | Sequential placement | 8, 15 | `precedesAction`, `respondsTo`, `expandsSequence` | InteractionAction ↔ InteractionAction | analytic/inferred |
| `io:preference-organization` | Preferred/dispreferred response organization | 15 | `PreferenceOrganizationAssessment` | ResponsePattern → PreferenceStatus | inferred, contestable |
| `io:repair` | Conversation repair | 8, 15 | `RepairEvent` with `repairsTroubleSource` | RepairTurn → TroubleSource | analytic/inferred |
| `io:self-repair` | Self-correction | 8, 15 | `RepairEvent` with same-agent constraint | Turn/TCU → Turn/TCU | analytic |
| `io:other-repair` | Other correction/clarification | 15 | `RepairEvent` with different-agent relation | Turn/TCU → Turn/TCU | analytic |
| `io:recipient-design` | Recipient design | 8, 15 | `RecipientDesignAssessment` | Utterance → RecipientModel | inferred, contestable |
| `io:alignment` | Structural alignment | 8, 15 | `alignsWithActivity` | Response → InteractionActivity | inferred |
| `io:affiliation` | Affective/evaluative affiliation | 8, 15 | `AffiliationAssessment` | Response → PriorStance | inferred, contestable |
| `io:face-work` | Face; face management | 8 | `FaceWorkEvent` | InteractionAction → SocialSelfImage | inferred, contestable |
| `io:politeness-strategy` | Politeness strategy | 8 | `PolitenessStrategyAssignment` | Utterance → StrategyType | inferred, culture-relative |
| `io:epistemic-stance` | Epistemic stance | 8 | `StanceAssignment` | Agent × Proposition → CommitmentDegree | inferred, contestable |
| `io:stance-triangle` | Evaluation-positioning-alignment | 8 | `StanceEvent` | Agent × Object × OtherAgent → StanceRelations | inferred |
| `io:backchannel` | Backchanneling | 15 | `BackchannelEvent` | ListenerTurn → PriorSpeakerTurn | analytic/inferred |
| `io:membership-categorization` | Membership categorization | 15 | `CategoryAssignment` | PersonReference → SocialCategory | inferred, contestable |
| `io:rhetorical-persuasion` | Available means of persuasion | 9 | `RhetoricalStrategyAssignment` | Utterance/Discourse → Strategy | inferred |
| `io:ethos` | Credibility appeal | 9 | `EthosAppeal` | Discourse → SpeakerCharacterClaim | inferred |
| `io:pathos` | Emotional appeal | 9 | `PathosAppeal` | Discourse → IntendedEmotion | inferred, contestable |
| `io:logos` | Reason/evidence appeal | 9 | `LogosAppeal` | Discourse → ArgumentStructure | analytic/inferred |
| `io:enthymeme` | Argument with implicit premise | 9 | `EnthymemeAnalysis` | Argument → UnstatedPremise | inferred, contestable |
| `io:identification` | Burkean identification | 9 | `IdentificationStrategy` | Discourse → SharedIdentityFrame | inferred |
| `io:dramatistic-pentad` | Act/agent/scene/agency/purpose | 9 | `DramatisticAnalysis` | NarrativeEvent → PentadRoles | analytic/inferred |
| `io:audience-adaptation` | Audience adaptation | 9 | `AudienceAdaptationAssessment` | Discourse → AudienceModel | inferred |
| `io:toulmin-argument` | Claim/data/warrant/backing/qualifier/rebuttal | 9 | `Argument` node with typed component edges | ArgumentComponentSet → Claim | analytic/inferred |
| `io:framing` | Frame analysis/framing effect | 9, 14, 18 | `FrameAssignment` | DiscourseElement → InterpretiveFrame | inferred, contestable |
| `io:metonymy` | Association-based transfer | 9, 18 | `MetonymicMapping` | SourceConcept → TargetConcept | inferred |
| `io:synecdoche` | Part/whole substitution | 9 | `PartWholeReferenceMapping` | Part/Whole → Whole/Part | inferred |
| `io:irony` | Nonliteral/oppositional meaning | 9 | `IronyInterpretation` | Utterance × Context → IntendedMeaning | inferred, highly contestable |
| `io:metalinguistic-function` | Language about language | 10 | `hasCommunicativeFunction(metalingual)` | Utterance → FunctionType | inferred |
| `io:jakobson-function` | Referential/emotive/conative/phatic/metalingual/poetic | 10 | `CommunicativeFunctionAssignment` | Utterance → FunctionType | inferred, multi-valued |
| `io:object-metalanguage` | Object language/metalanguage distinction | 10 | `describesLanguageLevel` | Expression → LanguageLevel | analytic |
| `io:gloss` | Glossing | 10 | `GlossAssignment` | Expression → Explanation | explicit/inferred |
| `io:definition` | Semantic regulation/definition | 10 | `DefinitionEvent` | Agent × Term → StipulatedMeaning | explicit |
| `io:quotation` | Quotation | 10 | `Quotation` with exact span links | SourceSpanSet → Quotation | explicit |
| `io:reported-speech` | Direct/indirect report | 10 | `ReportedSpeechEvent` | Reporter × PriorUtterance → Report | inferred/explicit |
| `io:free-indirect-discourse` | Blended narrator/character perspective | 10 | `PerspectiveBlendAssignment` | NarrativeSpan → PerspectiveSet | inferred |
| `io:poetic-function` | Foregrounding linguistic form | 10 | `PoeticFunctionAssignment` | Utterance → FormalPatternSet | inferred |
| `io:parallelism` | Repeated syntactic/semantic pattern | 10 | `ParallelStructureRelation` | Span ↔ Span | analytic |
| `io:self-reference` | Formal self-reference | 10 | `refersToSelf` plus language-level constraints | Expression → Expression/System | analytic |
| `io:presupposition` | Background assumption | 13 | `PresuppositionAssertion` / `presupposes` | Proposition/Utterance → Proposition | inferred, defeasible, contestable |
| `io:presupposition-projection` | Projection through embedding | 13 | `ProjectionAssessment` | EmbeddedStructure → PresuppositionSet | inferred |
| `io:entailment` | Logical/semantic consequence | 13 | `EntailmentAssertion` / `entails` | Proposition → Proposition | analytic relative to model |
| `io:common-ground` | Mutually recognized information | 13 | `CommonGroundState` | ParticipantGroup × Time → PropositionSet | inferred, contestable |
| `io:context-set` | Possible-world context set | 13 | `ContextSet` | Context → PossibilitySet | theory-relative |
| `io:relevance` | Effects/effort guided inference | 13 | `RelevanceAssessment` | Interpretation × Context → RelevanceScore/Reasons | inferred |
| `io:topic-focus` | Topic/focus; given/new information | 13 | `InformationStructureAssignment` | Utterance → Topic × Focus | inferred |
| `io:language-game` | Rule-governed use | 14 | `participatesInLanguageGame` | Utterance/Action → SocialPractice | inferred |
| `io:form-of-life` | Embedded social practice | 14 | `embeddedInFormOfLife` | LanguageGame → PracticeComplex | theoretical |
| `io:ethnography-communication` | Culturally situated speaking norms | 14 | `CommunicationNorm` | SpeechCommunity × EventType → Norm | empirical/inferred |
| `io:communicative-competence` | Appropriate-use competence | 14 | `CompetenceAssessment` | Agent × SpeechCommunity → Capability | empirical/inferred |
| `io:speech-community` | Shared language norms | 14 | `SpeechCommunity` | AgentGroup → NormSet | empirical/inferred |
| `io:community-practice` | Community of practice | 14 | `CommunityOfPractice` | AgentGroup → SharedActivity | empirical |
| `io:social-indexicality` | Form indexes social meaning | 14 | `indexesSocialMeaning` | LinguisticFeature → SocialMeaning | inferred, contestable |
| `io:register` | Register assignment | 14 | `RegisterAssignment` | Utterance × Situation → Register | inferred |
| `io:style-shift` | Style shifting | 14 | `StyleShiftEvent` | PriorStyle → NewStyle | analytic/inferred |
| `io:language-ideology` | Beliefs about language | 14 | `LanguageIdeologyClaim` | Agent/Institution → LanguageVarietyEvaluation | inferred/explicit |
| `io:discourse-power` | Discursive production of authority/categories | 14 | `PowerEffectAssessment` | DiscoursePractice → InstitutionalCategory/Authority | inferred, contestable |
| `io:symbolic-power` | Authorized linguistic force | 14 | `AuthorityCondition` | AgentRole × Institution → SpeechActValidity | analytic/inferred |
| `io:narrative-identity` | Identity construction through narrative | 14 | `NarrativeIdentityConstruction` | Narrative → IdentityClaim | inferred, contestable |
| `io:behaviorist-learning` | Reinforcement/habit formation | 17 | `LearningEvent(reinforcement)` | Stimulus × Response × Consequence → LearnedPattern | theory-relative |
| `io:usage-based-learning` | Usage-based acquisition | 17 | `ConstructionLearningEvent` | UsageInstances → Construction | empirical/inferred |
| `io:statistical-learning` | Statistical pattern extraction | 17 | `StatisticalLearningEvent` | InputDistribution → LearnedRegularity | empirical |
| `io:joint-attention` | Shared attention | 17 | `JointAttentionEvent` | Agent × Agent × Object/Event | observed/inferred |
| `io:intention-reading` | Communicative intention inference | 17 | `IntentionAssignment` | Learner × OtherAction → IntendedGoal | inferred |
| `io:social-scaffolding` | LASS/scaffolding/ZPD | 17 | `ScaffoldingEvent` | SupportingAgent × Learner × Task | observed/inferred |
| `io:cultural-transmission` | Imitation and cultural evolution | 17 | `TransmissionEvent` | Agent/Generation → Agent/Generation | empirical/inferred |
| `io:error-driven-learning` | Adjustment from mismatch/feedback | 17 | `LearningUpdateEvent` | PredictionError → ModelUpdate | analytic/empirical |
| `io:critical-period` | Developmental window | 17 | `DevelopmentalConstraintClaim` | Age/DevelopmentStage → AcquisitionCapacity | empirical/contested |
| `io:neural-plasticity` | Experience-dependent neural change | 17 | `PlasticityEvidenceAssertion` | TrainingEvent → NeuralChange | empirical |
| `io:argument-scheme` | Defeasible argument pattern | 19 | `ArgumentSchemeInstance` | PremiseSet → Claim | analytic/inferred |
| `io:narrative-persuasion` | Persuasion through narrative transportation/identity | 19 | `NarrativePersuasionAssessment` | Narrative → Belief/AttitudeEffect | evidential/inferred |
| `io:authority-construction` | Construction/invocation of authority | 19 | `AuthorityClaim` | Speaker/Source → AuthorityBasis | inferred, contestable |
| `io:propaganda-operation` | Coordinated manipulative persuasion operation | 19 | `PropagandaAssessment` | DiscourseCampaign → StrategySet | inferred, high-risk, contestable |
| `io:deliberation` | Structured debate/deliberation | 19 | `DeliberationEvent` | ParticipantSet × ProposalSet → Decision/Record | analytic |

## 3. Required graph relations

| Relation | Domain → Range | Reification requirement |
|---|---|---|
| `hasSourceSpan` | DerivedEntity → SourceSpan | Direct edge permitted. |
| `quotedFrom` | Quotation → SourceSpan | Direct edge; exact-text invariant. |
| `transformedBy` | DerivedEntity → TransformationEvent | Direct edge. |
| `usedContext` | Interpretation/Assessment → ContextSnapshot | Direct edge. |
| `assignedForce` | ForceAssignment → ForceType | ForceAssignment must be a node. |
| `presupposes` | PresuppositionAssertion → Proposition | Assertion node required for confidence, context, alternatives, and contestation. |
| `entails` | EntailmentAssertion → Proposition | Assertion node required unless relation is purely formal and rule-bound. |
| `implicates` | ImplicatureAssertion → Proposition | Assertion node always required. |
| `evokesFrame` | FrameAssignment → Frame | Assignment node required. |
| `mapsSourceToTarget` | ConceptualMapping → ConceptualDomain | Mapping node has source and target roles. |
| `corefersWith` | CoreferenceAssertion → ReferringExpression | Assertion node required. |
| `pairedWith` | AdjacencyPair → Turn | Pair node identifies first and second pair parts. |
| `repairsTroubleSource` | RepairEvent → Turn/TCU/Span | Event node required. |
| `indexesSocialMeaning` | SocialIndexicalityAssertion → SocialMeaning | Assertion node required. |
| `contestedBy` | ContestableRecord → ContestationEvent | Direct edge. |
| `supersededBy` | Record → RevisedRecord | Prior record remains retrievable. |
| `definesOperation` | OperationDefinitionOccurrence → CanonicalOperation | Direct edge. |
| `contrastsWith` | Theory/CanonicalOperation ↔ Theory/CanonicalOperation | Symmetric where appropriate. |
| `extends` | Theory/CanonicalOperation → Theory/CanonicalOperation | Directed. |
| `revisesConcept` | CanonicalOperationVersion → PriorVersion | Directed and provenance-bearing. |

## 4. Known supplied-source correction

| Supplied record | Corrected record | Preservation rule |
|---|---|---|
| “Laurel Karttunen”; repository identified as Linguistic Society of America | **Lauri Karttunen**, “Presuppositions of Compound Sentences,” *Linguistic Inquiry* 4(2), 169–193; journal published by MIT Press | Preserve the supplied occurrence, create a corrected occurrence, and link with `prov:wasRevisionOf` plus a correction basis. |

## 5. Completion criterion

The crosswalk is complete only when every source row in the canonical corpus has:

1. an immutable row occurrence identifier;
2. a source-status value (`supplied`, `corrected`, `verified`, or `synthesized`);
3. a link to one canonical operation or an explicit reason for remaining distinct;
4. a graph realization;
5. domain/range constraints;
6. inference and contestability classification;
7. citation provenance.
