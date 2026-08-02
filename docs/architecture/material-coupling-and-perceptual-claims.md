# Material Coupling and Perceptual Claims

**Status:** Consolidated architectural extension v0.1.0  
**Parent:** `docs/architecture/relational-definition-standard.md`

## 1. Physical connection

A perceiving locus is physically connected to what it sees through a causal chain of material interaction.

For ordinary vision:

1. light is emitted by a source;
2. photons interact with a material locus through reflection, scattering, absorption, transmission, or re-emission;
3. the resulting distribution of photons is modulated by that interaction and by illumination, geometry, medium, and motion;
4. a subset of those photons enters the eye and is focused onto the retina;
5. photon absorption by retinal photopigments initiates phototransduction;
6. retinal and neural processes transform the signal into a perceptual Claim configuration.

The perceived locus therefore contributes materially to the perceptual result. The perceiver does not generate the result without constraint, and the result is not a complete transfer of the thing itself.

## 2. Information terminology

The photons reaching the eye carry structured, causally correlated information produced by their interaction with the encountered locus.

`Optical coherence` has a narrower physical meaning concerning phase correlation and is not generally required for ordinary vision. The architectural term is therefore:

> photon-mediated transfer of structured, causally correlated information

This information is partial and condition-bound. It reflects the encountered locus under a particular illumination, angle, distance, medium, temporal state, sensory apparatus, and processing history.

## 3. Perception as inter-locus coupling

```text
Illumination source
  → photon interaction with encountered locus L₂
  → modulated photon field
  → retinal interaction at perceiving locus L₁
  → phototransduction and neural transformation
  → perceptual Claim C
```

The perceptual Claim is generated through the physical coupling of loci. It belongs exclusively to neither locus taken in isolation.

The encountered locus supplies material constraint and causal contribution. The perceiving locus supplies sensory organization, position, motion, prior structure, and transformation. The condition field supplies illumination, medium, geometry, time, and surrounding relations.

## 4. Architectural consequence

Perception is not modeled as an isolated subject privately representing an external object. It is modeled as a materially mediated Claim event arising through inter-locus coupling.

```text
PerceptualClaim(c)
:= Claim generated through a causal information-bearing relation
   between perceiving locus, encountered locus, and condition field
```

This coupling precedes explicit linguistic exchange. Language and later Claim work stabilize, compare, communicate, contest, and consolidate perceptual Claims that already arise through material relations.

## 5. Relation to communal construction

`Communal` must not be restricted to deliberate conversation or agreement. In this architecture it names participation in a shared material-relational event.

A thing seen participates causally without needing intention, language, or reciprocal recognition. Physical interaction supplies a real contribution to meaning construction before explicit social negotiation begins.

## 6. Limits

The photon-mediated signal does not transparently deliver every property of the encountered locus. It carries information conditioned by:

- illumination spectrum and direction;
- surface and material interaction;
- occlusion and medium;
- spatial and temporal sampling;
- retinal sensitivity;
- neural transformation;
- attention, movement, memory, and prior Claims.

The physical connection grounds perception while preserving the distinction between the encountered locus, the transmitted signal, and the resulting perceptual Claim.
