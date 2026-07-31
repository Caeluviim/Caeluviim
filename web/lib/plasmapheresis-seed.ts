import { createKnowledgeRecord, type KnowledgeRecord, type KnowledgeRecordInput } from "./knowledge";

const retrievedAt = "2026-07-16";

const constructionRule =
  "Seed record created from a named public source to establish the initial plasmapheresis coverage map; treat as a navigational provenance node until expanded into finer-grained claims.";

const seedInputs: KnowledgeRecordInput[] = [
  {
    recordType: "Definition",
    label: "Source Plasma is plasma collected by plasmapheresis for manufacturing",
    content:
      "U.S. regulation defines Source Plasma as the fluid portion of human blood collected by plasmapheresis and intended as source material for further manufacturing, excluding single-donor plasma products for intravenous use.",
    domains: ["law", "regulation", "medicine"],
    topics: [
      "plasmapheresis",
      "source plasma",
      "plasma manufacturing",
      "law",
      "medical procedure",
      "21 CFR 640.60",
    ],
    sourceTitle: "21 CFR 640.60 - Source Plasma",
    sourceUrl:
      "https://www.ecfr.gov/current/title-21/chapter-I/subchapter-F/part-640/subpart-G/section-640.60",
    sourceLocator: "21 CFR 640.60",
    sourceExcerpt:
      "fluid portion of human blood collected by plasmapheresis and intended as source material for further manufacturing use",
    constructionRule,
    jurisdiction: "United States",
    sourcePublishedAt: "current eCFR",
  },
  {
    recordType: "Process",
    label: "Regulatory procedure: blood removed, plasma separated, red cells returned",
    content:
      "The eCFR procedure model for plasmapheresis is a single-visit collection process: blood is removed from a donor, plasma is separated from formed elements, and at least red blood cells are returned.",
    domains: ["regulation", "medicine", "technology"],
    topics: [
      "plasmapheresis",
      "blood collection",
      "plasma separation",
      "red cell return",
      "biological processes",
      "medical procedure",
    ],
    sourceTitle: "21 CFR 640.65 - Plasmapheresis",
    sourceUrl:
      "https://www.ecfr.gov/current/title-21/chapter-I/subchapter-F/part-640/subpart-G/section-640.65",
    sourceLocator: "21 CFR 640.65(a)",
    sourceExcerpt:
      "blood is removed from a donor, the plasma separated from the formed elements",
    constructionRule,
    jurisdiction: "United States",
    sourcePublishedAt: "current eCFR",
  },
  {
    recordType: "Authority",
    label: "FDA accepts the June 2024 Circular for blood component labeling",
    content:
      "FDA recognizes the June 2024 Circular of Information as acceptable labeling instructions for administration and use of human blood and blood components intended for transfusion.",
    domains: ["regulation", "medicine", "law"],
    topics: ["plasma components", "blood component labeling", "FDA", "Circular of Information"],
    sourceTitle:
      "FDA: An Acceptable Circular of Information for the Use of Human Blood and Blood Components",
    sourceUrl:
      "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/acceptable-circular-information-use-human-blood-and-blood-components",
    sourceLocator: "FDA guidance page, June 2024 Circular recognition",
    sourceExcerpt:
      "provides specific labeling instructions for the administration and use of blood and blood components",
    constructionRule,
    jurisdiction: "United States",
    sourcePublishedAt: "2024-06",
  },
  {
    recordType: "Substance",
    label: "Blood plasma contains water, proteins, electrolytes, immunoglobulins, hormones, and vitamins",
    content:
      "Plasma is the liquid base of blood. Core constituents include water, coagulants such as fibrinogen, albumin and globulins, electrolytes, immunoglobulins, enzymes, hormones, and vitamins.",
    domains: ["biology", "medicine", "academia"],
    topics: [
      "plasma constituents",
      "plasma proteins",
      "albumin",
      "globulins",
      "fibrinogen",
      "immunoglobulins",
      "electrolytes",
      "hormones",
      "vitamins",
      "biological processes",
      "plasmapheresis",
    ],
    sourceTitle: "NCBI Bookshelf: Physiology, Blood Plasma",
    sourceUrl: "https://www.ncbi.nlm.nih.gov/books/NBK531504/",
    sourceLocator: "Introduction",
    sourceExcerpt:
      "Plasma contains 91% to 92% of water and 8% to 9% of solids.",
    constructionRule,
    sourcePublishedAt: "2023 update",
  },
  {
    recordType: "Substance",
    label: "Apheresis-derived plasma units may contain 400 to 600 mL",
    content:
      "The AABB Circular describes plasma components prepared from whole blood or apheresis collection and notes that apheresis-derived plasma units may contain larger volumes than typical whole-blood-derived units.",
    domains: ["medicine", "biology", "technology"],
    topics: ["plasma components", "apheresis collection", "PF24", "plasma proteins"],
    sourceTitle: "AABB Circular of Information for the Use of Human Blood and Blood Components",
    sourceUrl:
      "https://www.aabb.org/docs/default-source/default-document-library/resources/circular-of-information-watermark.pdf",
    sourceLocator: "Plasma Frozen Within 24 Hours After Phlebotomy section",
    sourceExcerpt:
      "apheresis-derived units may contain as much as 400 to 600 mL",
    constructionRule,
    jurisdiction: "United States",
    sourcePublishedAt: "2024-06",
  },
  {
    recordType: "Authority",
    label: "ASFA 2023 guidelines are the current evidence map for therapeutic apheresis",
    content:
      "The 2023 ninth edition ASFA special issue is a key clinical resource for deciding when therapeutic apheresis, including therapeutic plasma exchange, is indicated for human disease.",
    domains: ["medicine", "academia"],
    topics: [
      "therapeutic plasma exchange",
      "TPE",
      "ASFA guidelines",
      "apheresis indications",
      "academic literature",
      "plasmapheresis",
    ],
    sourceTitle: "PubMed: Guidelines on the Use of Therapeutic Apheresis in Clinical Practice",
    sourceUrl: "https://pubmed.ncbi.nlm.nih.gov/37017433/",
    sourceLocator: "Abstract, ninth special issue",
    sourceExcerpt:
      "key resource that guides the utilization of TA in the treatment of human disease",
    constructionRule,
    sourcePublishedAt: "2023",
  },
  {
    recordType: "Process",
    label: "Therapeutic plasma exchange removes patient plasma and replaces it with another fluid",
    content:
      "Therapeutic plasma exchange is an extracorporeal blood purification procedure that removes patient plasma and replaces it with a replacement fluid to address plasma-borne pathologic substances or deficiencies.",
    domains: ["medicine", "technology", "academia"],
    topics: [
      "therapeutic plasma exchange",
      "TPE",
      "extracorporeal blood purification",
      "dialysis analog",
      "replacement fluid",
      "plasmapheresis",
    ],
    sourceTitle: "Therapeutic Plasma Exchange: Current and Emerging Applications",
    sourceUrl: "https://pmc.ncbi.nlm.nih.gov/articles/PMC12292254/",
    sourceLocator: "Review introduction",
    sourceExcerpt:
      "current and emerging indications for TPE across cardiovascular, metabolic, neurological, inflammatory",
    constructionRule,
    sourcePublishedAt: "2025",
  },
  {
    recordType: "Observation",
    label: "TPE in intensive care is invasive and requires experienced monitoring",
    content:
      "ICU use of therapeutic plasma exchange can be lifesaving but carries adverse-event risk, so implementation depends on vascular access, replacement-fluid management, anticoagulation, monitoring, and experienced teams.",
    domains: ["medicine", "technology", "ethics"],
    topics: [
      "therapeutic plasma exchange",
      "TPE complications",
      "vascular access",
      "replacement fluid",
      "hypocalcemia",
      "risk",
      "plasmapheresis",
    ],
    sourceTitle: "Plasma exchange in the intensive care unit: a narrative review",
    sourceUrl: "https://pmc.ncbi.nlm.nih.gov/articles/PMC9372988/",
    sourceLocator: "Abstract",
    sourceExcerpt:
      "invasive procedure with risk of adverse events and complications",
    constructionRule,
    sourcePublishedAt: "2022",
  },
  {
    recordType: "Event",
    label: "The term plasmapheresis traces to Abel, Rowntree, and Turner in 1914",
    content:
      "The historical term plasmapheresis traces to the 1914 paper by Abel, Rowntree, and Turner on plasma removal with return of corpuscles.",
    domains: ["history", "academia"],
    topics: ["plasmapheresis history", "Abel Rowntree Turner", "1914", "plasma removal"],
    sourceTitle: "PubMed: Plasma removal with return of corpuscles (plasmapheresis)",
    sourceUrl: "https://pubmed.ncbi.nlm.nih.gov/10160881/",
    sourceLocator: "Bibliographic record",
    sourceExcerpt:
      "Plasma removal with return of corpuscles (plasmapheresis)",
    constructionRule,
    sourcePublishedAt: "1914",
  },
  {
    recordType: "Authority",
    label: "WHO frames plasma-derived medicinal products as an international access and supply problem",
    content:
      "WHO guidance treats plasma-derived medicinal products as a global supply, safety, and access issue, with special emphasis on increasing quality plasma production and fractionation capacity in low- and middle-income countries.",
    domains: ["international", "regulation", "economics", "ethics"],
    topics: [
      "plasma-derived medicinal products",
      "PDMP",
      "fractionation",
      "international practice",
      "LMIC",
      "global access",
      "plasmapheresis",
    ],
    sourceTitle:
      "WHO: Guidance on increasing supplies of plasma-derived medicinal products in LMICs",
    sourceUrl: "https://www.who.int/publications/i/item/9789240021815",
    sourceLocator: "Publication overview",
    sourceExcerpt:
      "increase the production of quality and safe plasma from voluntary non-remunerated donors",
    constructionRule,
    sourcePublishedAt: "2021",
  },
  {
    recordType: "Document",
    label: "WHO info sheet: plasma may be recovered or collected by apheresis for medicinal products",
    content:
      "WHO describes plasma-derived medicinal products as manufactured from human blood plasma, with plasma obtained either from whole-blood donations as recovered plasma or by apheresis procedures as source plasma.",
    domains: ["international", "medicine", "economics"],
    topics: [
      "plasma-derived medicinal products",
      "source plasma",
      "recovered plasma",
      "apheresis procedures",
      "fractionation",
      "plasmapheresis",
    ],
    sourceTitle: "WHO: Ensuring the Quality and Safety of Plasma Derived Medicinal Products",
    sourceUrl:
      "https://cdn.who.int/media/docs/default-source/biologicals/blood-products/infosheet-plasma-derived.pdf?download=true&sfvrsn=9b6a9ca9_4",
    sourceLocator: "WHO biologicals info sheet",
    sourceExcerpt:
      "Plasma can be obtained from whole blood donations or by apheresis procedures",
    constructionRule,
    sourcePublishedAt: "2003",
  },
  {
    recordType: "Authority",
    label: "FDA regulates fractionated plasma products as approved blood products",
    content:
      "FDA maintains a regulated category for fractionated plasma products, linking plasma collection and fractionation to licensed biologics, approvals, and supporting product documents.",
    domains: ["regulation", "law", "economics", "medicine"],
    topics: [
      "fractionated plasma products",
      "plasma-derived therapeutics",
      "FDA biologics",
      "plasma economy",
      "economics",
      "plasmapheresis",
    ],
    sourceTitle: "FDA: Fractionated Plasma Products",
    sourceUrl:
      "https://www.fda.gov/vaccines-blood-biologics/approved-blood-products/fractionated-plasma-products",
    sourceLocator: "FDA approved blood products page",
    sourceExcerpt:
      "The following products are regulated as Fractionated Plasma Products",
    constructionRule,
    jurisdiction: "United States",
    sourcePublishedAt: "2026",
  },
  {
    recordType: "Observation",
    label: "U.S. paid donor source plasma reached about 72 million liters in 2023",
    content:
      "A 2025 plasma supply analysis reports that approximately 72 million liters of plasma were harvested from the U.S. paid donor source sector in 2023, making the United States central to global source-plasma supply.",
    domains: ["economics", "international", "social"],
    topics: [
      "source plasma supply",
      "paid plasma donation",
      "plasma economy",
      "United States",
      "2023 plasma volume",
      "plasmapheresis",
    ],
    sourceTitle:
      "Securing commitment and control for the supply of plasma-derived medicines",
    sourceUrl: "https://pmc.ncbi.nlm.nih.gov/articles/PMC11839246/",
    sourceLocator: "Supply-volume discussion",
    sourceExcerpt:
      "approximately 72 million litres of plasma was harvested from the US paid donor source sector in 2023",
    constructionRule,
    sourcePublishedAt: "2025",
  },
  {
    recordType: "Theory",
    label: "Plasma donation intersects with poverty, compensation, and access to plasma medicines",
    content:
      "Socioeconomic analysis of plasma donation links source plasma collection to compensation, poverty exposure, plasma protein therapy supply, and questions about who bears collection burdens versus who receives therapeutic benefits.",
    domains: ["social", "ethics", "economics", "law"],
    topics: [
      "plasma donation poverty",
      "paid plasma donation",
      "plasma protein therapies",
      "ethics",
      "access",
      "plasmapheresis",
    ],
    sourceTitle: "The Interlinkage between Blood Plasma Donation and Poverty in the United States",
    sourceUrl:
      "https://sites.fordschool.umich.edu/poverty2021/files/2022/07/Blood-Plasma-and-Poverty.pdf",
    sourceLocator: "Policy report introduction",
    sourceExcerpt:
      "Plasma is used in medical therapies called plasma protein therapies",
    constructionRule,
    jurisdiction: "United States",
    sourcePublishedAt: "2021",
  },
  {
    recordType: "Protocol",
    label: "Manual plasmapheresis depends on donor identification before red-cell return",
    content:
      "FDA inspection guidance identifies correct donor identification before red-cell return as the critical manual plasmapheresis control point, because the procedure separates plasma and returns cellular components.",
    domains: ["technology", "regulation", "medicine", "ethics"],
    topics: [
      "manual plasmapheresis",
      "red cell return",
      "donor identification",
      "inspection guidance",
      "operational details",
      "plasmapheresis",
    ],
    sourceTitle: "FDA Guide to Inspections of Source Plasma Establishments - Section 2",
    sourceUrl:
      "https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/inspection-guides/section-2",
    sourceLocator: "Reinfusion of red blood cells",
    sourceExcerpt:
      "most critical element in manual plasmapheresis is the proper identification of the donor",
    constructionRule,
    jurisdiction: "United States",
    sourcePublishedAt: "2024",
  },
];

let seedPromise: Promise<KnowledgeRecord[]> | null = null;

export function getPlasmapheresisSeedRecords() {
  seedPromise ??= Promise.all(
    seedInputs.map(async (input) => ({
      ...(await createKnowledgeRecord(input)),
      sourceRetrievedAt: `${retrievedAt}T00:00:00.000Z`,
    })),
  );
  return seedPromise;
}
