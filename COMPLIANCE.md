# HIPAA & India's DPDP Act — Reference

Two regimes that both govern patient data but work on fundamentally different
logic. HIPAA gives you a **bright line** for de-identification; DPDP gives you
**none** and regulates the processing instead.

*Engineering reference, not legal advice. Verify with counsel before relying on it.*

---

## Part 1 — HIPAA (United States)

**Statute:** Health Insurance Portability and Accountability Act, 1996
**Privacy Rule:** 45 CFR Parts 160 and 164 · **De-identification:** § 164.514

### Scope & roles

| Attribute | Detail |
|---|---|
| Applies to | **Covered Entities** (providers, health plans, clearinghouses) and their **Business Associates** |
| Not a general privacy law | Sectoral — health data only |
| Vendor mechanism | **Business Associate Agreement (BAA)** — required before a vendor touches PHI |
| What is PHI | Individually identifiable health information, in any form |
| Breach notification | Individuals: without unreasonable delay, **≤60 days** from discovery. HHS: annually, or within 60 days if ≥500 individuals affected |
| Penalties | Tiered civil monetary penalties by culpability, with annual caps; criminal liability for knowing misuse |
| Territorial | US persons and entities; relevant only if you handle US patient data |

### The 18 Safe Harbor identifiers — § 164.514(b)(2)(i)

Remove **all 18**, for the individual *and* their relatives, employers and
household members, and the data is no longer PHI.

| # | Identifier |
|---|---|
| A | Names |
| B | All geographic subdivisions smaller than a State — street address, city, county, precinct, ZIP |
| C | All elements of dates **except year** — birth, admission, discharge, death; and all ages over 89 |
| D | Telephone numbers |
| E | Fax numbers |
| F | Email addresses |
| G | Social Security numbers |
| H | Medical record numbers |
| I | Health plan beneficiary numbers |
| J | Account numbers |
| K | Certificate and licence numbers |
| L | Vehicle identifiers and serial numbers, including licence plates |
| M | Device identifiers and serial numbers |
| N | Web URLs |
| O | IP addresses |
| P | Biometric identifiers, including finger and voice prints |
| Q | Full-face photographs and comparable images |
| R | **Any other unique identifying number, characteristic, or code** |

**Two threshold rules worth knowing:**

- **ZIP** — the first three digits may be retained *only* if that 3-digit area contains **more than 20,000 people**; otherwise it becomes `000`.
- **Age** — all ages over 89 aggregate into a single `90 or older` bucket.

**(R) is the catch-all that matters.** Accession numbers, requisition numbers,
internal MRNs and barcode values all land here.

### The three de-identification routes

| Route | Citation | How it works |
|---|---|---|
| **Safe Harbor** | § 164.514(b)(2) | Remove all 18 **and** have no *actual knowledge* the remainder could re-identify. No statistician needed. |
| **Expert Determination** | § 164.514(b)(1) | A qualified expert certifies the re-identification risk is "very small", and documents the method. |
| **Limited Data Set** | § 164.514(e) | Not de-identification — some identifiers retained, permitted uses only, requires a data use agreement. |

> **The trap:** Safe Harbor requires the 18 items removed **and** no actual
> knowledge of re-identifiability. A probabilistic ML redactor cannot certify the
> second condition. Automated redaction reduces exposure; it does not by itself
> deliver Safe Harbor.

---

## Part 2 — DPDP Act (India)

**Statute:** Digital Personal Data Protection Act, 2023 (Act No. 22 of 2023)
**Rules:** DPDP Rules, 2025 — notified November 2025

### Scope & roles

| Attribute | Detail |
|---|---|
| Applies to | **Digital** personal data. Omnibus — every sector, not just health |
| Extraterritorial | Yes, if processing relates to offering goods or services to individuals in India |
| **Data Principal** | The individual the data is about |
| **Data Fiduciary** | Whoever determines the purpose and means of processing — *a clinic or EMR operator is one* |
| **Data Processor** | Processes on a Fiduciary's behalf, under contract |
| **Significant Data Fiduciary (SDF)** | Designated by Government on volume/sensitivity/risk. Extra duties: DPO based in India, independent auditor, annual DPIA and audit |
| **Consent Manager** | Registered with the Data Protection Board (Rule 4); gives Data Principals one place to grant, review and withdraw consent |
| Regulator | Data Protection Board of India |
| Breach notification | Board: **without delay**, then a detailed report within **72 hours**. Affected Data Principals: promptly, in plain language — what happened, what it means, what to do |
| Enforcement | Monetary penalties only. **No criminal liability, no private right of action** |

### ⚠️ Two attributes that surprise people

1. **No "sensitive personal data" category.** Unlike GDPR and unlike India's own
   earlier SPDI Rules 2011, DPDP has **no special tier for health data**. Medical
   records are governed by the same rules as an email address. There is no
   heightened lawful-basis requirement to satisfy — and no reduced one either.
2. **No prescribed de-identification method.** Truly anonymised data falls
   outside the Act, but the Act does not define a procedure or a checklist.
   There is no Safe Harbour equivalent. Whether data is anonymised is a judgment
   you must be able to defend.

### Lawful bases

- **Consent** — must be free, specific, informed, unconditional and unambiguous, given by clear affirmative action, for a stated purpose, and **withdrawable at any time** with comparable ease.
- **Certain legitimate uses** (§ 7) — a defined list including voluntary provision of data, medical emergencies, epidemics and threats to public health, employment purposes, and specified State functions.

### Data Principal rights

| Right | Substance |
|---|---|
| Access | Summary of personal data held and processing activities |
| Correction | Correction, completion and updating |
| Erasure | Deletion, unless retention is legally required |
| Grievance redressal | Fiduciary must provide a mechanism before escalation to the Board |
| **Nomination** | Nominate another person to exercise rights on death or incapacity — distinctive to DPDP |

### Children

Verifiable parental consent required for anyone under 18. Tracking, behavioural
monitoring and targeted advertising directed at children are prohibited.

### Cross-border transfer — § 16

Transfer is **permitted by default**, except to countries the Central Government
restricts by notification. A **blocklist**, not GDPR's adequacy allowlist — more
permissive, but the restricted list can change. Sector regulators may impose
stricter localisation on top.

### Penalties — Schedule to the Act (indicative maxima)

| Failure | Up to |
|---|---|
| Reasonable security safeguards, resulting in a breach | **₹250 crore** |
| Notifying a personal data breach | ₹200 crore |
| Obligations relating to children | ₹200 crore |
| Additional obligations of a Significant Data Fiduciary | ₹150 crore |
| Any other provision | ₹50 crore |
| Data Principal's own duties (e.g. frivolous complaints) | ₹10,000 |

Penalties stack — inadequate safeguards **and** failure to notify are separate.

### Compliance timeline

| Date | What takes effect |
|---|---|
| **13 Nov 2025** | Data Protection Board constituted; core definitions live |
| **13 Nov 2026** | Enforcement powers, penalty framework, Consent Manager registration |
| **13 May 2027** | **Full compliance** — consent, notice, security safeguards, Data Principal rights |

---

## Part 3 — Side by side

| | HIPAA | DPDP Act |
|---|---|---|
| Type | Sectoral (health) | Omnibus (all personal data) |
| Health data treated specially | Yes, by definition | **No special tier** |
| De-identification method | **Prescribed** — 18 identifiers, or expert determination | **None prescribed** |
| "Remove these and you're out of scope" | Yes — Safe Harbor | No equivalent |
| Your role | Covered Entity / Business Associate | **Data Fiduciary** |
| Consent | Not always needed (treatment, payment, operations) | Consent or a listed legitimate use; **withdrawable** |
| Vendor mechanism | BAA | Contract with Data Processor |
| Breach clock | ≤60 days to individuals | **72 hours** to the Board |
| Cross-border | Not directly addressed | § 16 blocklist |
| Criminal liability | Yes | **No** |
| Private lawsuits | No private right of action | **No private right of action** |
| Erasure right | Limited (amendment, not deletion) | **Yes** |

### What this means in practice

- **Redaction is defence in depth under both, and compliance under neither.**
  HIPAA needs the 18 identifiers gone *plus* no actual knowledge of
  re-identifiability. DPDP does not recognise redaction as a status change at all
  — it regulates how you process, consent, secure and honour rights.
- **DPDP's obligations are procedural, and redaction touches none of them.**
  Consent capture, notice, withdrawal, erasure, nomination, 72-hour breach
  reporting — no redaction technology discharges any of these.
- **Minimisation beats redaction.** Data never collected cannot leak, cannot be
  mis-redacted, and does not need erasing on request. It is the only control that
  satisfies both regimes at once.
- **If you serve Indian patients only, DPDP is the binding regime** — and its
  hardest requirement is consent infrastructure, not de-identification.

---

## Sources

**HIPAA** — [HHS de-identification guidance](https://www.hhs.gov/hipaa/for-professionals/special-topics/de-identification/index.html) · [45 CFR § 164.514(b)](https://www.bricker.com/insights/resources/key/HIPAA-Privacy-Regulations-Other-Requirements-Relating-to-Uses-and-Disclosures-of-Protected-Health-Information-Requirements-for-De-Identification-of-Protected-Health-Information-164-514-b) · [Safe Harbor reference (Network for Public Health Law)](https://www.networkforphl.org/wp-content/uploads/2020/01/De-Identification_HIPAASafeHarbor-10-1-19.pdf)

**DPDP** — [DPDP Rules 2025 (PIB)](https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/nov/doc20251117695301.pdf) · [EY compliance guide](https://www.ey.com/en_in/insights/cybersecurity/decoding-the-digital-personal-data-protection-act-2023) · [Rules 2025 (Wikipedia)](https://en.wikipedia.org/wiki/Digital_Personal_Data_Protection_Rules,_2025) · [Breach reporting timeline (MediaNama)](https://www.medianama.com/2025/11/223-data-breach-reporting-timeline-of-dpdp-rules-2025-explained/) · [Health data & DPDP (Mondaq)](https://www.mondaq.com/pdf/1722484.pdf)
