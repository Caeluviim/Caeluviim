import Caeluviim.Cycle2

/-!
# RRKC Cycle 2 — Constructive span coherence

This module constructs the canonical span comparison maps from selected
pullback universal properties. It does not assume a `SpanCoherenceProof`.
-/

namespace Caeluviim.RRKC.Cycle2

universe u

/-- Reassociate four composable structural morphisms while retaining the
middle pair as a visible subexpression. -/
theorem FacetCategory.comp_four_middle
    {sig : StaticSignature}
    (baseCategory : FacetCategory sig)
    {A B C D E : baseCategory.Facet}
    (first : baseCategory.Hom A B)
    (second : baseCategory.Hom B C)
    (third : baseCategory.Hom C D)
    (fourth : baseCategory.Hom D E) :
    baseCategory.comp
        (baseCategory.comp
          (baseCategory.comp first second)
          third)
        fourth =
      baseCategory.comp
        first
        (baseCategory.comp
          (baseCategory.comp second third)
          fourth) := by
  calc
    baseCategory.comp
        (baseCategory.comp
          (baseCategory.comp first second)
          third)
        fourth =
        baseCategory.comp
          (baseCategory.comp
            first
            (baseCategory.comp second third))
          fourth := by
      rw [baseCategory.comp_assoc first second third]
    _ = baseCategory.comp
          first
          (baseCategory.comp
            (baseCategory.comp second third)
            fourth) :=
      baseCategory.comp_assoc
        first
        (baseCategory.comp second third)
        fourth

/-- Fully right-associate five composable structural morphisms. -/
theorem FacetCategory.comp_five_right
    {sig : StaticSignature}
    (baseCategory : FacetCategory sig)
    {A B C D E F : baseCategory.Facet}
    (first : baseCategory.Hom A B)
    (second : baseCategory.Hom B C)
    (third : baseCategory.Hom C D)
    (fourth : baseCategory.Hom D E)
    (fifth : baseCategory.Hom E F) :
    baseCategory.comp
        (baseCategory.comp
          (baseCategory.comp
            (baseCategory.comp first second)
            third)
          fourth)
        fifth =
      baseCategory.comp
        first
        (baseCategory.comp
          second
          (baseCategory.comp third (baseCategory.comp fourth fifth))) := by
  calc
    baseCategory.comp
        (baseCategory.comp
          (baseCategory.comp
            (baseCategory.comp first second)
            third)
          fourth)
        fifth =
        baseCategory.comp
          (baseCategory.comp
            (baseCategory.comp first second)
            third)
          (baseCategory.comp fourth fifth) :=
      baseCategory.comp_assoc
        (baseCategory.comp
          (baseCategory.comp first second)
          third)
        fourth
        fifth
    _ = baseCategory.comp
          (baseCategory.comp first second)
          (baseCategory.comp third (baseCategory.comp fourth fifth)) :=
      baseCategory.comp_assoc
        (baseCategory.comp first second)
        third
        (baseCategory.comp fourth fifth)
    _ = baseCategory.comp
          first
          (baseCategory.comp
            second
            (baseCategory.comp third (baseCategory.comp fourth fifth))) :=
      baseCategory.comp_assoc
        first
        second
        (baseCategory.comp third (baseCategory.comp fourth fifth))

/-- The canonical left unitor induced by the selected pullback of an identity
map and a span's source leg. -/
def canonicalLeftUnitor
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B : baseCategory.Facet}
    (span : StructuralSpan baseCategory A B) :
    SpanIsomorphism
      (StructuralSpan.compose
        selected
        (StructuralSpan.identity A)
        span)
      span := by
  let pullback :=
    selected.select (baseCategory.id A) span.sourceLeg
  have inverseCompatibility :
      baseCategory.comp span.sourceLeg (baseCategory.id A) =
        baseCategory.comp (baseCategory.id span.apex) span.sourceLeg := by
    calc
      baseCategory.comp span.sourceLeg (baseCategory.id A) =
          span.sourceLeg :=
        baseCategory.comp_id span.sourceLeg
      _ = baseCategory.comp
            (baseCategory.id span.apex)
            span.sourceLeg := by
        exact (baseCategory.id_comp span.sourceLeg).symm
  let inverse :=
    pullback.lift
      span.sourceLeg
      (baseCategory.id span.apex)
      inverseCompatibility
  refine
    { hom := pullback.snd
      inv := inverse
      homInv := ?_
      invHom := ?_
      sourceCommutes := ?_
      targetCommutes := ?_
      inverseSourceCommutes := ?_
      inverseTargetCommutes := ?_ }
  · apply pullback.hom_ext
    · calc
        baseCategory.comp
            (baseCategory.comp pullback.snd inverse)
            pullback.fst =
            baseCategory.comp
              pullback.snd
              (baseCategory.comp inverse pullback.fst) :=
          baseCategory.comp_assoc pullback.snd inverse pullback.fst
        _ = baseCategory.comp pullback.snd span.sourceLeg := by
          rw [pullback.lift_fst]
        _ = baseCategory.comp pullback.fst (baseCategory.id A) :=
          pullback.commutes.symm
        _ = pullback.fst :=
          baseCategory.comp_id pullback.fst
        _ = baseCategory.comp
              (baseCategory.id pullback.apex)
              pullback.fst := by
          exact (baseCategory.id_comp pullback.fst).symm
    · calc
        baseCategory.comp
            (baseCategory.comp pullback.snd inverse)
            pullback.snd =
            baseCategory.comp
              pullback.snd
              (baseCategory.comp inverse pullback.snd) :=
          baseCategory.comp_assoc pullback.snd inverse pullback.snd
        _ = baseCategory.comp
              pullback.snd
              (baseCategory.id span.apex) := by
          rw [pullback.lift_snd]
        _ = pullback.snd :=
          baseCategory.comp_id pullback.snd
        _ = baseCategory.comp
              (baseCategory.id pullback.apex)
              pullback.snd := by
          exact (baseCategory.id_comp pullback.snd).symm
  · change
      baseCategory.comp
          (pullback.lift
            span.sourceLeg
            (baseCategory.id span.apex)
            inverseCompatibility)
          pullback.snd =
        baseCategory.id span.apex
    exact
      pullback.lift_snd
        span.sourceLeg
        (baseCategory.id span.apex)
        inverseCompatibility
  · exact pullback.commutes.symm
  · rfl
  · calc
      baseCategory.comp
          inverse
          (baseCategory.comp pullback.fst (baseCategory.id A)) =
          baseCategory.comp
            (baseCategory.comp inverse pullback.fst)
            (baseCategory.id A) := by
        exact
          (baseCategory.comp_assoc
            inverse
            pullback.fst
            (baseCategory.id A)).symm
      _ = baseCategory.comp span.sourceLeg (baseCategory.id A) := by
        rw [pullback.lift_fst]
      _ = span.sourceLeg :=
        baseCategory.comp_id span.sourceLeg
  · calc
      baseCategory.comp
          inverse
          (baseCategory.comp pullback.snd span.targetLeg) =
          baseCategory.comp
            (baseCategory.comp inverse pullback.snd)
            span.targetLeg := by
        exact
          (baseCategory.comp_assoc
            inverse
            pullback.snd
            span.targetLeg).symm
      _ = baseCategory.comp
            (baseCategory.id span.apex)
            span.targetLeg := by
        rw [pullback.lift_snd]
      _ = span.targetLeg :=
        baseCategory.id_comp span.targetLeg

/-- The canonical right unitor induced by the selected pullback of a span's
target leg and an identity map. -/
def canonicalRightUnitor
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B : baseCategory.Facet}
    (span : StructuralSpan baseCategory A B) :
    SpanIsomorphism
      (StructuralSpan.compose
        selected
        span
        (StructuralSpan.identity B))
      span := by
  let pullback :=
    selected.select span.targetLeg (baseCategory.id B)
  have inverseCompatibility :
      baseCategory.comp
          (baseCategory.id span.apex)
          span.targetLeg =
        baseCategory.comp span.targetLeg (baseCategory.id B) := by
    calc
      baseCategory.comp
          (baseCategory.id span.apex)
          span.targetLeg =
          span.targetLeg :=
        baseCategory.id_comp span.targetLeg
      _ = baseCategory.comp span.targetLeg (baseCategory.id B) := by
        exact (baseCategory.comp_id span.targetLeg).symm
  let inverse :=
    pullback.lift
      (baseCategory.id span.apex)
      span.targetLeg
      inverseCompatibility
  refine
    { hom := pullback.fst
      inv := inverse
      homInv := ?_
      invHom := ?_
      sourceCommutes := ?_
      targetCommutes := ?_
      inverseSourceCommutes := ?_
      inverseTargetCommutes := ?_ }
  · apply pullback.hom_ext
    · calc
        baseCategory.comp
            (baseCategory.comp pullback.fst inverse)
            pullback.fst =
            baseCategory.comp
              pullback.fst
              (baseCategory.comp inverse pullback.fst) :=
          baseCategory.comp_assoc pullback.fst inverse pullback.fst
        _ = baseCategory.comp
              pullback.fst
              (baseCategory.id span.apex) := by
          rw [pullback.lift_fst]
        _ = pullback.fst :=
          baseCategory.comp_id pullback.fst
        _ = baseCategory.comp
              (baseCategory.id pullback.apex)
              pullback.fst := by
          exact (baseCategory.id_comp pullback.fst).symm
    · calc
        baseCategory.comp
            (baseCategory.comp pullback.fst inverse)
            pullback.snd =
            baseCategory.comp
              pullback.fst
              (baseCategory.comp inverse pullback.snd) :=
          baseCategory.comp_assoc pullback.fst inverse pullback.snd
        _ = baseCategory.comp pullback.fst span.targetLeg := by
          rw [pullback.lift_snd]
        _ = baseCategory.comp pullback.snd (baseCategory.id B) :=
          pullback.commutes
        _ = pullback.snd :=
          baseCategory.comp_id pullback.snd
        _ = baseCategory.comp
              (baseCategory.id pullback.apex)
              pullback.snd := by
          exact (baseCategory.id_comp pullback.snd).symm
  · change
      baseCategory.comp
          (pullback.lift
            (baseCategory.id span.apex)
            span.targetLeg
            inverseCompatibility)
          pullback.fst =
        baseCategory.id span.apex
    exact
      pullback.lift_fst
        (baseCategory.id span.apex)
        span.targetLeg
        inverseCompatibility
  · rfl
  · exact pullback.commutes
  · calc
      baseCategory.comp
          inverse
          (baseCategory.comp pullback.fst span.sourceLeg) =
          baseCategory.comp
            (baseCategory.comp inverse pullback.fst)
            span.sourceLeg := by
        exact
          (baseCategory.comp_assoc
            inverse
            pullback.fst
            span.sourceLeg).symm
      _ = baseCategory.comp
            (baseCategory.id span.apex)
            span.sourceLeg := by
        rw [pullback.lift_fst]
      _ = span.sourceLeg :=
        baseCategory.id_comp span.sourceLeg
  · calc
      baseCategory.comp
          inverse
          (baseCategory.comp pullback.snd (baseCategory.id B)) =
          baseCategory.comp
            (baseCategory.comp inverse pullback.snd)
            (baseCategory.id B) := by
        exact
          (baseCategory.comp_assoc
            inverse
            pullback.snd
            (baseCategory.id B)).symm
      _ = baseCategory.comp span.targetLeg (baseCategory.id B) := by
        rw [pullback.lift_snd]
      _ = span.targetLeg :=
        baseCategory.comp_id span.targetLeg

/-- The canonical forward associator apex map from `(first * second) * third`
to `first * (second * third)`. -/
def canonicalAssociatorHom
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D : baseCategory.Facet}
    (first : StructuralSpan baseCategory A B)
    (second : StructuralSpan baseCategory B C)
    (third : StructuralSpan baseCategory C D) :
    baseCategory.Hom
      (StructuralSpan.compose
        selected
        (StructuralSpan.compose selected first second)
        third).apex
      (StructuralSpan.compose
        selected
        first
        (StructuralSpan.compose selected second third)).apex := by
  let firstSecond :=
    selected.select first.targetLeg second.sourceLeg
  let secondThird :=
    selected.select second.targetLeg third.sourceLeg
  let leftPullback :=
    selected.select
      (baseCategory.comp firstSecond.snd second.targetLeg)
      third.sourceLeg
  let rightPullback :=
    selected.select
      first.targetLeg
      (baseCategory.comp secondThird.fst second.sourceLeg)
  have middleCompatibility :
      baseCategory.comp
          (baseCategory.comp leftPullback.fst firstSecond.snd)
          second.targetLeg =
        baseCategory.comp leftPullback.snd third.sourceLeg := by
    calc
      baseCategory.comp
          (baseCategory.comp leftPullback.fst firstSecond.snd)
          second.targetLeg =
          baseCategory.comp
            leftPullback.fst
            (baseCategory.comp firstSecond.snd second.targetLeg) :=
        baseCategory.comp_assoc
          leftPullback.fst
          firstSecond.snd
          second.targetLeg
      _ = baseCategory.comp leftPullback.snd third.sourceLeg :=
        leftPullback.commutes
  let toSecondThird :=
    secondThird.lift
      (baseCategory.comp leftPullback.fst firstSecond.snd)
      leftPullback.snd
      middleCompatibility
  have outerCompatibility :
      baseCategory.comp
          (baseCategory.comp leftPullback.fst firstSecond.fst)
          first.targetLeg =
        baseCategory.comp
          toSecondThird
          (baseCategory.comp secondThird.fst second.sourceLeg) := by
    calc
      baseCategory.comp
          (baseCategory.comp leftPullback.fst firstSecond.fst)
          first.targetLeg =
          baseCategory.comp
            leftPullback.fst
            (baseCategory.comp firstSecond.fst first.targetLeg) :=
        baseCategory.comp_assoc
          leftPullback.fst
          firstSecond.fst
          first.targetLeg
      _ = baseCategory.comp
            leftPullback.fst
            (baseCategory.comp firstSecond.snd second.sourceLeg) := by
        rw [firstSecond.commutes]
      _ = baseCategory.comp
            (baseCategory.comp leftPullback.fst firstSecond.snd)
            second.sourceLeg := by
        exact
          (baseCategory.comp_assoc
            leftPullback.fst
            firstSecond.snd
            second.sourceLeg).symm
      _ = baseCategory.comp
            (baseCategory.comp toSecondThird secondThird.fst)
            second.sourceLeg := by
        rw [secondThird.lift_fst]
      _ = baseCategory.comp
            toSecondThird
            (baseCategory.comp secondThird.fst second.sourceLeg) :=
        baseCategory.comp_assoc
          toSecondThird
          secondThird.fst
          second.sourceLeg
  exact
    rightPullback.lift
      (baseCategory.comp leftPullback.fst firstSecond.fst)
      toSecondThird
      outerCompatibility

/-- The canonical inverse associator apex map. -/
def canonicalAssociatorInv
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D : baseCategory.Facet}
    (first : StructuralSpan baseCategory A B)
    (second : StructuralSpan baseCategory B C)
    (third : StructuralSpan baseCategory C D) :
    baseCategory.Hom
      (StructuralSpan.compose
        selected
        first
        (StructuralSpan.compose selected second third)).apex
      (StructuralSpan.compose
        selected
        (StructuralSpan.compose selected first second)
        third).apex := by
  let firstSecond :=
    selected.select first.targetLeg second.sourceLeg
  let secondThird :=
    selected.select second.targetLeg third.sourceLeg
  let leftPullback :=
    selected.select
      (baseCategory.comp firstSecond.snd second.targetLeg)
      third.sourceLeg
  let rightPullback :=
    selected.select
      first.targetLeg
      (baseCategory.comp secondThird.fst second.sourceLeg)
  have firstMiddleCompatibility :
      baseCategory.comp rightPullback.fst first.targetLeg =
        baseCategory.comp
          (baseCategory.comp rightPullback.snd secondThird.fst)
          second.sourceLeg := by
    calc
      baseCategory.comp rightPullback.fst first.targetLeg =
          baseCategory.comp
            rightPullback.snd
            (baseCategory.comp secondThird.fst second.sourceLeg) :=
        rightPullback.commutes
      _ = baseCategory.comp
            (baseCategory.comp rightPullback.snd secondThird.fst)
            second.sourceLeg := by
        exact
          (baseCategory.comp_assoc
            rightPullback.snd
            secondThird.fst
            second.sourceLeg).symm
  let toFirstSecond :=
    firstSecond.lift
      rightPullback.fst
      (baseCategory.comp rightPullback.snd secondThird.fst)
      firstMiddleCompatibility
  have outerCompatibility :
      baseCategory.comp
          toFirstSecond
          (baseCategory.comp firstSecond.snd second.targetLeg) =
        baseCategory.comp
          (baseCategory.comp rightPullback.snd secondThird.snd)
          third.sourceLeg := by
    calc
      baseCategory.comp
          toFirstSecond
          (baseCategory.comp firstSecond.snd second.targetLeg) =
          baseCategory.comp
            (baseCategory.comp toFirstSecond firstSecond.snd)
            second.targetLeg := by
        exact
          (baseCategory.comp_assoc
            toFirstSecond
            firstSecond.snd
            second.targetLeg).symm
      _ = baseCategory.comp
            (baseCategory.comp rightPullback.snd secondThird.fst)
            second.targetLeg := by
        rw [firstSecond.lift_snd]
      _ = baseCategory.comp
            rightPullback.snd
            (baseCategory.comp secondThird.fst second.targetLeg) :=
        baseCategory.comp_assoc
          rightPullback.snd
          secondThird.fst
          second.targetLeg
      _ = baseCategory.comp
            rightPullback.snd
            (baseCategory.comp secondThird.snd third.sourceLeg) := by
        rw [secondThird.commutes]
      _ = baseCategory.comp
            (baseCategory.comp rightPullback.snd secondThird.snd)
            third.sourceLeg := by
        exact
          (baseCategory.comp_assoc
            rightPullback.snd
            secondThird.snd
            third.sourceLeg).symm
  exact
    leftPullback.lift
      toFirstSecond
      (baseCategory.comp rightPullback.snd secondThird.snd)
      outerCompatibility

/-- The canonical associator preserves the first component projection. -/
theorem canonicalAssociatorHom_first
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D : baseCategory.Facet}
    (first : StructuralSpan baseCategory A B)
    (second : StructuralSpan baseCategory B C)
    (third : StructuralSpan baseCategory C D) :
    let firstSecond :=
      selected.select first.targetLeg second.sourceLeg
    let secondThird :=
      selected.select second.targetLeg third.sourceLeg
    let leftPullback :=
      selected.select
        (baseCategory.comp firstSecond.snd second.targetLeg)
        third.sourceLeg
    let rightPullback :=
      selected.select
        first.targetLeg
        (baseCategory.comp secondThird.fst second.sourceLeg)
    baseCategory.comp
        (canonicalAssociatorHom selected first second third)
        rightPullback.fst =
      baseCategory.comp leftPullback.fst firstSecond.fst := by
  dsimp
  apply
    (selected.select
      first.targetLeg
      (baseCategory.comp
        (selected.select second.targetLeg third.sourceLeg).fst
        second.sourceLeg)).lift_fst

/-- The canonical associator preserves the middle component projection. -/
theorem canonicalAssociatorHom_second
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D : baseCategory.Facet}
    (first : StructuralSpan baseCategory A B)
    (second : StructuralSpan baseCategory B C)
    (third : StructuralSpan baseCategory C D) :
    let firstSecond :=
      selected.select first.targetLeg second.sourceLeg
    let secondThird :=
      selected.select second.targetLeg third.sourceLeg
    let leftPullback :=
      selected.select
        (baseCategory.comp firstSecond.snd second.targetLeg)
        third.sourceLeg
    let rightPullback :=
      selected.select
        first.targetLeg
        (baseCategory.comp secondThird.fst second.sourceLeg)
    baseCategory.comp
        (baseCategory.comp
          (canonicalAssociatorHom selected first second third)
          rightPullback.snd)
        secondThird.fst =
      baseCategory.comp leftPullback.fst firstSecond.snd := by
  dsimp
  unfold canonicalAssociatorHom
  rw [
    (selected.select
      first.targetLeg
      (baseCategory.comp
        (selected.select second.targetLeg third.sourceLeg).fst
        second.sourceLeg)).lift_snd
  ]
  apply
    (selected.select second.targetLeg third.sourceLeg).lift_fst

/-- The canonical associator preserves the third component projection. -/
theorem canonicalAssociatorHom_third
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D : baseCategory.Facet}
    (first : StructuralSpan baseCategory A B)
    (second : StructuralSpan baseCategory B C)
    (third : StructuralSpan baseCategory C D) :
    let firstSecond :=
      selected.select first.targetLeg second.sourceLeg
    let secondThird :=
      selected.select second.targetLeg third.sourceLeg
    let leftPullback :=
      selected.select
        (baseCategory.comp firstSecond.snd second.targetLeg)
        third.sourceLeg
    let rightPullback :=
      selected.select
        first.targetLeg
        (baseCategory.comp secondThird.fst second.sourceLeg)
    baseCategory.comp
        (baseCategory.comp
          (canonicalAssociatorHom selected first second third)
          rightPullback.snd)
        secondThird.snd =
      leftPullback.snd := by
  dsimp
  unfold canonicalAssociatorHom
  rw [
    (selected.select
      first.targetLeg
      (baseCategory.comp
        (selected.select second.targetLeg third.sourceLeg).fst
        second.sourceLeg)).lift_snd
  ]
  apply
    (selected.select second.targetLeg third.sourceLeg).lift_snd

/-- The inverse associator preserves the first component projection. -/
theorem canonicalAssociatorInv_first
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D : baseCategory.Facet}
    (first : StructuralSpan baseCategory A B)
    (second : StructuralSpan baseCategory B C)
    (third : StructuralSpan baseCategory C D) :
    let firstSecond :=
      selected.select first.targetLeg second.sourceLeg
    let secondThird :=
      selected.select second.targetLeg third.sourceLeg
    let leftPullback :=
      selected.select
        (baseCategory.comp firstSecond.snd second.targetLeg)
        third.sourceLeg
    let rightPullback :=
      selected.select
        first.targetLeg
        (baseCategory.comp secondThird.fst second.sourceLeg)
    baseCategory.comp
        (baseCategory.comp
          (canonicalAssociatorInv selected first second third)
          leftPullback.fst)
        firstSecond.fst =
      rightPullback.fst := by
  dsimp
  unfold canonicalAssociatorInv
  rw [
    (selected.select
      (baseCategory.comp
        (selected.select first.targetLeg second.sourceLeg).snd
        second.targetLeg)
      third.sourceLeg).lift_fst
  ]
  apply
    (selected.select first.targetLeg second.sourceLeg).lift_fst

/-- The inverse associator preserves the middle component projection. -/
theorem canonicalAssociatorInv_second
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D : baseCategory.Facet}
    (first : StructuralSpan baseCategory A B)
    (second : StructuralSpan baseCategory B C)
    (third : StructuralSpan baseCategory C D) :
    let firstSecond :=
      selected.select first.targetLeg second.sourceLeg
    let secondThird :=
      selected.select second.targetLeg third.sourceLeg
    let leftPullback :=
      selected.select
        (baseCategory.comp firstSecond.snd second.targetLeg)
        third.sourceLeg
    let rightPullback :=
      selected.select
        first.targetLeg
        (baseCategory.comp secondThird.fst second.sourceLeg)
    baseCategory.comp
        (baseCategory.comp
          (canonicalAssociatorInv selected first second third)
          leftPullback.fst)
        firstSecond.snd =
      baseCategory.comp rightPullback.snd secondThird.fst := by
  dsimp
  unfold canonicalAssociatorInv
  rw [
    (selected.select
      (baseCategory.comp
        (selected.select first.targetLeg second.sourceLeg).snd
        second.targetLeg)
      third.sourceLeg).lift_fst
  ]
  apply
    (selected.select first.targetLeg second.sourceLeg).lift_snd

/-- The inverse associator preserves the third component projection. -/
theorem canonicalAssociatorInv_third
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D : baseCategory.Facet}
    (first : StructuralSpan baseCategory A B)
    (second : StructuralSpan baseCategory B C)
    (third : StructuralSpan baseCategory C D) :
    let firstSecond :=
      selected.select first.targetLeg second.sourceLeg
    let secondThird :=
      selected.select second.targetLeg third.sourceLeg
    let leftPullback :=
      selected.select
        (baseCategory.comp firstSecond.snd second.targetLeg)
        third.sourceLeg
    let rightPullback :=
      selected.select
        first.targetLeg
        (baseCategory.comp secondThird.fst second.sourceLeg)
    baseCategory.comp
        (canonicalAssociatorInv selected first second third)
        leftPullback.snd =
      baseCategory.comp rightPullback.snd secondThird.snd := by
  dsimp
  apply
    (selected.select
      (baseCategory.comp
        (selected.select first.targetLeg second.sourceLeg).snd
        second.targetLeg)
      third.sourceLeg).lift_snd

/-- The canonical associator span isomorphism derived entirely from selected
pullback universal properties. -/
def canonicalAssociator
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D : baseCategory.Facet}
    (first : StructuralSpan baseCategory A B)
    (second : StructuralSpan baseCategory B C)
    (third : StructuralSpan baseCategory C D) :
    SpanIsomorphism
      (StructuralSpan.compose
        selected
        (StructuralSpan.compose selected first second)
        third)
      (StructuralSpan.compose
        selected
        first
        (StructuralSpan.compose selected second third)) := by
  let firstSecond :=
    selected.select first.targetLeg second.sourceLeg
  let secondThird :=
    selected.select second.targetLeg third.sourceLeg
  let leftPullback :=
    selected.select
      (baseCategory.comp firstSecond.snd second.targetLeg)
      third.sourceLeg
  let rightPullback :=
    selected.select
      first.targetLeg
      (baseCategory.comp secondThird.fst second.sourceLeg)
  let hom :=
    canonicalAssociatorHom selected first second third
  let inv :=
    canonicalAssociatorInv selected first second third
  have homFirst :
      baseCategory.comp hom rightPullback.fst =
        baseCategory.comp leftPullback.fst firstSecond.fst :=
    canonicalAssociatorHom_first selected first second third
  have homSecond :
      baseCategory.comp
          (baseCategory.comp hom rightPullback.snd)
          secondThird.fst =
        baseCategory.comp leftPullback.fst firstSecond.snd :=
    canonicalAssociatorHom_second selected first second third
  have homThird :
      baseCategory.comp
          (baseCategory.comp hom rightPullback.snd)
          secondThird.snd =
        leftPullback.snd :=
    canonicalAssociatorHom_third selected first second third
  have invFirst :
      baseCategory.comp
          (baseCategory.comp inv leftPullback.fst)
          firstSecond.fst =
        rightPullback.fst :=
    canonicalAssociatorInv_first selected first second third
  have invSecond :
      baseCategory.comp
          (baseCategory.comp inv leftPullback.fst)
          firstSecond.snd =
        baseCategory.comp rightPullback.snd secondThird.fst :=
    canonicalAssociatorInv_second selected first second third
  have invThird :
      baseCategory.comp inv leftPullback.snd =
        baseCategory.comp rightPullback.snd secondThird.snd :=
    canonicalAssociatorInv_third selected first second third
  refine
    { hom := hom
      inv := inv
      homInv := ?_
      invHom := ?_
      sourceCommutes := ?_
      targetCommutes := ?_
      inverseSourceCommutes := ?_
      inverseTargetCommutes := ?_ }
  · apply leftPullback.hom_ext
    · apply firstSecond.hom_ext
      · calc
          baseCategory.comp
              (baseCategory.comp
                (baseCategory.comp hom inv)
                leftPullback.fst)
              firstSecond.fst =
              baseCategory.comp
                hom
                (baseCategory.comp
                  (baseCategory.comp inv leftPullback.fst)
                  firstSecond.fst) := by
            calc
              baseCategory.comp
                  (baseCategory.comp
                    (baseCategory.comp hom inv)
                    leftPullback.fst)
                  firstSecond.fst =
                  baseCategory.comp
                    (baseCategory.comp hom inv)
                    (baseCategory.comp leftPullback.fst firstSecond.fst) :=
                baseCategory.comp_assoc
                  (baseCategory.comp hom inv)
                  leftPullback.fst
                  firstSecond.fst
              _ = baseCategory.comp
                    hom
                    (baseCategory.comp
                      inv
                      (baseCategory.comp
                        leftPullback.fst
                        firstSecond.fst)) :=
                baseCategory.comp_assoc
                  hom
                  inv
                  (baseCategory.comp leftPullback.fst firstSecond.fst)
              _ = baseCategory.comp
                    hom
                    (baseCategory.comp
                      (baseCategory.comp inv leftPullback.fst)
                      firstSecond.fst) := by
                rw [
                  baseCategory.comp_assoc
                    inv
                    leftPullback.fst
                    firstSecond.fst
                ]
          _ = baseCategory.comp hom rightPullback.fst := by
            rw [invFirst]
          _ = baseCategory.comp leftPullback.fst firstSecond.fst :=
            homFirst
          _ = baseCategory.comp
                (baseCategory.comp
                  (baseCategory.id leftPullback.apex)
                  leftPullback.fst)
                firstSecond.fst := by
            rw [baseCategory.id_comp]
      · calc
          baseCategory.comp
              (baseCategory.comp
                (baseCategory.comp hom inv)
                leftPullback.fst)
              firstSecond.snd =
              baseCategory.comp
                hom
                (baseCategory.comp
                  (baseCategory.comp inv leftPullback.fst)
                  firstSecond.snd) := by
            calc
              baseCategory.comp
                  (baseCategory.comp
                    (baseCategory.comp hom inv)
                    leftPullback.fst)
                  firstSecond.snd =
                  baseCategory.comp
                    (baseCategory.comp hom inv)
                    (baseCategory.comp leftPullback.fst firstSecond.snd) :=
                baseCategory.comp_assoc
                  (baseCategory.comp hom inv)
                  leftPullback.fst
                  firstSecond.snd
              _ = baseCategory.comp
                    hom
                    (baseCategory.comp
                      inv
                      (baseCategory.comp
                        leftPullback.fst
                        firstSecond.snd)) :=
                baseCategory.comp_assoc
                  hom
                  inv
                  (baseCategory.comp leftPullback.fst firstSecond.snd)
              _ = baseCategory.comp
                    hom
                    (baseCategory.comp
                      (baseCategory.comp inv leftPullback.fst)
                      firstSecond.snd) := by
                rw [
                  baseCategory.comp_assoc
                    inv
                    leftPullback.fst
                    firstSecond.snd
                ]
          _ = baseCategory.comp
                hom
                (baseCategory.comp rightPullback.snd secondThird.fst) := by
            rw [invSecond]
          _ = baseCategory.comp
                (baseCategory.comp hom rightPullback.snd)
                secondThird.fst := by
            exact
              (baseCategory.comp_assoc
                hom
                rightPullback.snd
                secondThird.fst).symm
          _ = baseCategory.comp leftPullback.fst firstSecond.snd :=
            homSecond
          _ = baseCategory.comp
                (baseCategory.comp
                  (baseCategory.id leftPullback.apex)
                  leftPullback.fst)
                firstSecond.snd := by
            rw [baseCategory.id_comp]
    · calc
        baseCategory.comp
            (baseCategory.comp hom inv)
            leftPullback.snd =
            baseCategory.comp
              hom
              (baseCategory.comp inv leftPullback.snd) :=
          baseCategory.comp_assoc hom inv leftPullback.snd
        _ = baseCategory.comp
              hom
              (baseCategory.comp rightPullback.snd secondThird.snd) := by
          rw [invThird]
        _ = baseCategory.comp
              (baseCategory.comp hom rightPullback.snd)
              secondThird.snd := by
          exact
            (baseCategory.comp_assoc
              hom
              rightPullback.snd
              secondThird.snd).symm
        _ = leftPullback.snd :=
          homThird
        _ = baseCategory.comp
              (baseCategory.id leftPullback.apex)
              leftPullback.snd := by
          exact (baseCategory.id_comp leftPullback.snd).symm
  · apply rightPullback.hom_ext
    · calc
        baseCategory.comp
            (baseCategory.comp inv hom)
            rightPullback.fst =
            baseCategory.comp
              inv
              (baseCategory.comp hom rightPullback.fst) :=
          baseCategory.comp_assoc inv hom rightPullback.fst
        _ = baseCategory.comp
              inv
              (baseCategory.comp leftPullback.fst firstSecond.fst) := by
          rw [homFirst]
        _ = baseCategory.comp
              (baseCategory.comp inv leftPullback.fst)
              firstSecond.fst := by
          exact
            (baseCategory.comp_assoc
              inv
              leftPullback.fst
              firstSecond.fst).symm
        _ = rightPullback.fst :=
          invFirst
        _ = baseCategory.comp
              (baseCategory.id rightPullback.apex)
              rightPullback.fst := by
          exact (baseCategory.id_comp rightPullback.fst).symm
    · apply secondThird.hom_ext
      · calc
          baseCategory.comp
              (baseCategory.comp
                (baseCategory.comp inv hom)
                rightPullback.snd)
              secondThird.fst =
              baseCategory.comp
                inv
                (baseCategory.comp
                  (baseCategory.comp hom rightPullback.snd)
                  secondThird.fst) := by
            calc
              baseCategory.comp
                  (baseCategory.comp
                    (baseCategory.comp inv hom)
                    rightPullback.snd)
                  secondThird.fst =
                  baseCategory.comp
                    (baseCategory.comp inv hom)
                    (baseCategory.comp rightPullback.snd secondThird.fst) :=
                baseCategory.comp_assoc
                  (baseCategory.comp inv hom)
                  rightPullback.snd
                  secondThird.fst
              _ = baseCategory.comp
                    inv
                    (baseCategory.comp
                      hom
                      (baseCategory.comp
                        rightPullback.snd
                        secondThird.fst)) :=
                baseCategory.comp_assoc
                  inv
                  hom
                  (baseCategory.comp rightPullback.snd secondThird.fst)
              _ = baseCategory.comp
                    inv
                    (baseCategory.comp
                      (baseCategory.comp hom rightPullback.snd)
                      secondThird.fst) := by
                rw [
                  baseCategory.comp_assoc
                    hom
                    rightPullback.snd
                    secondThird.fst
                ]
          _ = baseCategory.comp
                inv
                (baseCategory.comp leftPullback.fst firstSecond.snd) := by
            rw [homSecond]
          _ = baseCategory.comp
                (baseCategory.comp inv leftPullback.fst)
                firstSecond.snd := by
            exact
              (baseCategory.comp_assoc
                inv
                leftPullback.fst
                firstSecond.snd).symm
          _ = baseCategory.comp rightPullback.snd secondThird.fst :=
            invSecond
          _ = baseCategory.comp
                (baseCategory.comp
                  (baseCategory.id rightPullback.apex)
                  rightPullback.snd)
                secondThird.fst := by
            rw [baseCategory.id_comp]
      · calc
          baseCategory.comp
              (baseCategory.comp
                (baseCategory.comp inv hom)
                rightPullback.snd)
              secondThird.snd =
              baseCategory.comp
                inv
                (baseCategory.comp
                  (baseCategory.comp hom rightPullback.snd)
                  secondThird.snd) := by
            calc
              baseCategory.comp
                  (baseCategory.comp
                    (baseCategory.comp inv hom)
                    rightPullback.snd)
                  secondThird.snd =
                  baseCategory.comp
                    (baseCategory.comp inv hom)
                    (baseCategory.comp rightPullback.snd secondThird.snd) :=
                baseCategory.comp_assoc
                  (baseCategory.comp inv hom)
                  rightPullback.snd
                  secondThird.snd
              _ = baseCategory.comp
                    inv
                    (baseCategory.comp
                      hom
                      (baseCategory.comp
                        rightPullback.snd
                        secondThird.snd)) :=
                baseCategory.comp_assoc
                  inv
                  hom
                  (baseCategory.comp rightPullback.snd secondThird.snd)
              _ = baseCategory.comp
                    inv
                    (baseCategory.comp
                      (baseCategory.comp hom rightPullback.snd)
                      secondThird.snd) := by
                rw [
                  baseCategory.comp_assoc
                    hom
                    rightPullback.snd
                    secondThird.snd
                ]
          _ = baseCategory.comp inv leftPullback.snd := by
            rw [homThird]
          _ = baseCategory.comp rightPullback.snd secondThird.snd :=
            invThird
          _ = baseCategory.comp
                (baseCategory.comp
                  (baseCategory.id rightPullback.apex)
                  rightPullback.snd)
                secondThird.snd := by
            rw [baseCategory.id_comp]
  · calc
      baseCategory.comp
          hom
          (baseCategory.comp rightPullback.fst first.sourceLeg) =
          baseCategory.comp
            (baseCategory.comp hom rightPullback.fst)
            first.sourceLeg := by
        exact
          (baseCategory.comp_assoc
            hom
            rightPullback.fst
            first.sourceLeg).symm
      _ = baseCategory.comp
            (baseCategory.comp leftPullback.fst firstSecond.fst)
            first.sourceLeg := by
        rw [homFirst]
      _ = baseCategory.comp
            leftPullback.fst
            (baseCategory.comp firstSecond.fst first.sourceLeg) :=
        baseCategory.comp_assoc
          leftPullback.fst
          firstSecond.fst
          first.sourceLeg
  · calc
      baseCategory.comp
          hom
          (baseCategory.comp
            rightPullback.snd
            (baseCategory.comp secondThird.snd third.targetLeg)) =
          baseCategory.comp
            (baseCategory.comp hom rightPullback.snd)
            (baseCategory.comp secondThird.snd third.targetLeg) := by
        exact
          (baseCategory.comp_assoc
            hom
            rightPullback.snd
            (baseCategory.comp
              secondThird.snd
              third.targetLeg)).symm
      _ = baseCategory.comp
            (baseCategory.comp
              (baseCategory.comp hom rightPullback.snd)
              secondThird.snd)
            third.targetLeg := by
        exact
          (baseCategory.comp_assoc
            (baseCategory.comp hom rightPullback.snd)
            secondThird.snd
            third.targetLeg).symm
      _ = baseCategory.comp leftPullback.snd third.targetLeg := by
        rw [homThird]
  · calc
      baseCategory.comp
          inv
          (baseCategory.comp
            leftPullback.fst
            (baseCategory.comp firstSecond.fst first.sourceLeg)) =
          baseCategory.comp
            (baseCategory.comp inv leftPullback.fst)
            (baseCategory.comp firstSecond.fst first.sourceLeg) := by
        exact
          (baseCategory.comp_assoc
            inv
            leftPullback.fst
            (baseCategory.comp
              firstSecond.fst
              first.sourceLeg)).symm
      _ = baseCategory.comp
            (baseCategory.comp
              (baseCategory.comp inv leftPullback.fst)
              firstSecond.fst)
            first.sourceLeg := by
        exact
          (baseCategory.comp_assoc
            (baseCategory.comp inv leftPullback.fst)
            firstSecond.fst
            first.sourceLeg).symm
      _ = baseCategory.comp rightPullback.fst first.sourceLeg := by
        rw [invFirst]
  · calc
      baseCategory.comp
          inv
          (baseCategory.comp leftPullback.snd third.targetLeg) =
          baseCategory.comp
            (baseCategory.comp inv leftPullback.snd)
            third.targetLeg := by
        exact
          (baseCategory.comp_assoc
            inv
            leftPullback.snd
            third.targetLeg).symm
      _ = baseCategory.comp
            (baseCategory.comp rightPullback.snd secondThird.snd)
            third.targetLeg := by
        rw [invThird]
      _ = baseCategory.comp
            rightPullback.snd
            (baseCategory.comp secondThird.snd third.targetLeg) :=
        baseCategory.comp_assoc
          rightPullback.snd
          secondThird.snd
          third.targetLeg

/-- The comparison data canonically determined by a selected pullback
operation. -/
def canonicalSpanComparisonData
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory) :
    SpanComparisonData selected where
  leftUnitor := canonicalLeftUnitor selected
  rightUnitor := canonicalRightUnitor selected
  associator := canonicalAssociator selected

/-- Naturality equation for chosen left unitors. -/
def SpanLeftUnitorNaturality
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    {selected : SelectedPullbacks baseCategory}
    (comparisons : SpanComparisonData selected) : Prop :=
  ∀ {A B : baseCategory.Facet}
    {first second : StructuralSpan baseCategory A B}
    (alpha : SpanTwoCell first second),
    SpanTwoCell.vertical
        (SpanTwoCell.horizontal
          selected
          (SpanTwoCell.identity (StructuralSpan.identity A))
          alpha)
        (comparisons.leftUnitor second).homCell =
      SpanTwoCell.vertical
        (comparisons.leftUnitor first).homCell
        alpha

/-- Naturality equation for chosen right unitors. -/
def SpanRightUnitorNaturality
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    {selected : SelectedPullbacks baseCategory}
    (comparisons : SpanComparisonData selected) : Prop :=
  ∀ {A B : baseCategory.Facet}
    {first second : StructuralSpan baseCategory A B}
    (alpha : SpanTwoCell first second),
    SpanTwoCell.vertical
        (SpanTwoCell.horizontal
          selected
          alpha
          (SpanTwoCell.identity (StructuralSpan.identity B)))
        (comparisons.rightUnitor second).homCell =
      SpanTwoCell.vertical
        (comparisons.rightUnitor first).homCell
        alpha

/-- The canonical left unitor is natural. -/
theorem canonicalLeftUnitor_naturality
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory) :
    SpanLeftUnitorNaturality
      (canonicalSpanComparisonData selected) := by
  intro A B first second alpha
  apply SpanTwoCell.ext
  exact
    SpanTwoCell.horizontal_second_projection
      selected
      (SpanTwoCell.identity (StructuralSpan.identity A))
      alpha

/-- The canonical right unitor is natural. -/
theorem canonicalRightUnitor_naturality
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory) :
    SpanRightUnitorNaturality
      (canonicalSpanComparisonData selected) := by
  intro A B first second alpha
  apply SpanTwoCell.ext
  exact
    SpanTwoCell.horizontal_first_projection
      selected
      alpha
      (SpanTwoCell.identity (StructuralSpan.identity B))

/-- Extensionality for arrows into the left-associated triple composite. -/
theorem leftAssociatedTriple_hom_ext
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D : baseCategory.Facet}
    (first : StructuralSpan baseCategory A B)
    (second : StructuralSpan baseCategory B C)
    (third : StructuralSpan baseCategory C D)
    {Q : baseCategory.Facet}
    (left right :
      baseCategory.Hom
        Q
        (StructuralSpan.compose
          selected
          (StructuralSpan.compose selected first second)
          third).apex)
    (firstProjection :
      let firstSecond :=
        selected.select first.targetLeg second.sourceLeg
      let outer :=
        selected.select
          (baseCategory.comp firstSecond.snd second.targetLeg)
          third.sourceLeg
      baseCategory.comp
          (baseCategory.comp left outer.fst)
          firstSecond.fst =
        baseCategory.comp
          (baseCategory.comp right outer.fst)
          firstSecond.fst)
    (secondProjection :
      let firstSecond :=
        selected.select first.targetLeg second.sourceLeg
      let outer :=
        selected.select
          (baseCategory.comp firstSecond.snd second.targetLeg)
          third.sourceLeg
      baseCategory.comp
          (baseCategory.comp left outer.fst)
          firstSecond.snd =
        baseCategory.comp
          (baseCategory.comp right outer.fst)
          firstSecond.snd)
    (thirdProjection :
      let firstSecond :=
        selected.select first.targetLeg second.sourceLeg
      let outer :=
        selected.select
          (baseCategory.comp firstSecond.snd second.targetLeg)
          third.sourceLeg
      baseCategory.comp left outer.snd =
        baseCategory.comp right outer.snd) :
    left = right := by
  let firstSecond :=
    selected.select first.targetLeg second.sourceLeg
  let outer :=
    selected.select
      (baseCategory.comp firstSecond.snd second.targetLeg)
      third.sourceLeg
  apply outer.hom_ext
  · apply firstSecond.hom_ext
    · exact firstProjection
    · exact secondProjection
  · exact thirdProjection

/-- Extensionality for arrows into the right-associated triple composite. -/
theorem rightAssociatedTriple_hom_ext
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D : baseCategory.Facet}
    (first : StructuralSpan baseCategory A B)
    (second : StructuralSpan baseCategory B C)
    (third : StructuralSpan baseCategory C D)
    {Q : baseCategory.Facet}
    (left right :
      baseCategory.Hom
        Q
        (StructuralSpan.compose
          selected
          first
          (StructuralSpan.compose selected second third)).apex)
    (firstProjection :
      let secondThird :=
        selected.select second.targetLeg third.sourceLeg
      let outer :=
        selected.select
          first.targetLeg
          (baseCategory.comp secondThird.fst second.sourceLeg)
      baseCategory.comp left outer.fst =
        baseCategory.comp right outer.fst)
    (secondProjection :
      let secondThird :=
        selected.select second.targetLeg third.sourceLeg
      let outer :=
        selected.select
          first.targetLeg
          (baseCategory.comp secondThird.fst second.sourceLeg)
      baseCategory.comp
          (baseCategory.comp left outer.snd)
          secondThird.fst =
        baseCategory.comp
          (baseCategory.comp right outer.snd)
          secondThird.fst)
    (thirdProjection :
      let secondThird :=
        selected.select second.targetLeg third.sourceLeg
      let outer :=
        selected.select
          first.targetLeg
          (baseCategory.comp secondThird.fst second.sourceLeg)
      baseCategory.comp
          (baseCategory.comp left outer.snd)
          secondThird.snd =
        baseCategory.comp
          (baseCategory.comp right outer.snd)
          secondThird.snd) :
    left = right := by
  let secondThird :=
    selected.select second.targetLeg third.sourceLeg
  let outer :=
    selected.select
      first.targetLeg
      (baseCategory.comp secondThird.fst second.sourceLeg)
  apply outer.hom_ext
  · exact firstProjection
  · apply secondThird.hom_ext
    · exact secondProjection
    · exact thirdProjection

/-- First flattened projection of a horizontally composed left-associated
triple. -/
theorem horizontalLeftAssociated_first
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D : baseCategory.Facet}
    {first₀ first₁ : StructuralSpan baseCategory A B}
    {second₀ second₁ : StructuralSpan baseCategory B C}
    {third₀ third₁ : StructuralSpan baseCategory C D}
    (alpha : SpanTwoCell first₀ first₁)
    (beta : SpanTwoCell second₀ second₁)
    (gamma : SpanTwoCell third₀ third₁) :
    let firstSecond₀ :=
      selected.select first₀.targetLeg second₀.sourceLeg
    let firstSecond₁ :=
      selected.select first₁.targetLeg second₁.sourceLeg
    let outer₀ :=
      selected.select
        (baseCategory.comp firstSecond₀.snd second₀.targetLeg)
        third₀.sourceLeg
    let outer₁ :=
      selected.select
        (baseCategory.comp firstSecond₁.snd second₁.targetLeg)
        third₁.sourceLeg
    let horizontalInner :=
      SpanTwoCell.horizontal selected alpha beta
    let horizontalOuter :=
      SpanTwoCell.horizontal selected horizontalInner gamma
    baseCategory.comp
        (baseCategory.comp horizontalOuter.arrow outer₁.fst)
        firstSecond₁.fst =
      baseCategory.comp
        (baseCategory.comp outer₀.fst firstSecond₀.fst)
        alpha.arrow := by
  dsimp
  calc
    baseCategory.comp
        (baseCategory.comp
          (SpanTwoCell.horizontal
            selected
            (SpanTwoCell.horizontal selected alpha beta)
            gamma).arrow
          (selected.select
            (baseCategory.comp
              (selected.select
                first₁.targetLeg
                second₁.sourceLeg).snd
              second₁.targetLeg)
            third₁.sourceLeg).fst)
        (selected.select first₁.targetLeg second₁.sourceLeg).fst =
        baseCategory.comp
          (baseCategory.comp
            (selected.select
              (baseCategory.comp
                (selected.select
                  first₀.targetLeg
                  second₀.sourceLeg).snd
                second₀.targetLeg)
              third₀.sourceLeg).fst
            (SpanTwoCell.horizontal selected alpha beta).arrow)
          (selected.select first₁.targetLeg second₁.sourceLeg).fst := by
      exact
        congrArg
          (fun arrow =>
            baseCategory.comp
              arrow
              (selected.select
                first₁.targetLeg
                second₁.sourceLeg).fst)
          (SpanTwoCell.horizontal_first_projection
            selected
            (SpanTwoCell.horizontal selected alpha beta)
            gamma)
    _ = baseCategory.comp
          (selected.select
            (baseCategory.comp
              (selected.select
                first₀.targetLeg
                second₀.sourceLeg).snd
              second₀.targetLeg)
            third₀.sourceLeg).fst
          (baseCategory.comp
            (SpanTwoCell.horizontal selected alpha beta).arrow
            (selected.select first₁.targetLeg second₁.sourceLeg).fst) :=
      baseCategory.comp_assoc
        (selected.select
          (baseCategory.comp
            (selected.select
              first₀.targetLeg
              second₀.sourceLeg).snd
            second₀.targetLeg)
          third₀.sourceLeg).fst
        (SpanTwoCell.horizontal selected alpha beta).arrow
        (selected.select first₁.targetLeg second₁.sourceLeg).fst
    _ = baseCategory.comp
          (selected.select
            (baseCategory.comp
              (selected.select
                first₀.targetLeg
                second₀.sourceLeg).snd
              second₀.targetLeg)
            third₀.sourceLeg).fst
          (baseCategory.comp
            (selected.select first₀.targetLeg second₀.sourceLeg).fst
            alpha.arrow) := by
      rw [
        SpanTwoCell.horizontal_first_projection
          selected
          alpha
          beta
      ]
    _ = baseCategory.comp
          (baseCategory.comp
            (selected.select
              (baseCategory.comp
                (selected.select
                  first₀.targetLeg
                  second₀.sourceLeg).snd
                second₀.targetLeg)
              third₀.sourceLeg).fst
            (selected.select first₀.targetLeg second₀.sourceLeg).fst)
          alpha.arrow := by
      exact
        (baseCategory.comp_assoc
          (selected.select
            (baseCategory.comp
              (selected.select
                first₀.targetLeg
                second₀.sourceLeg).snd
              second₀.targetLeg)
            third₀.sourceLeg).fst
          (selected.select first₀.targetLeg second₀.sourceLeg).fst
          alpha.arrow).symm

/-- Middle flattened projection of a horizontally composed left-associated
triple. -/
theorem horizontalLeftAssociated_second
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D : baseCategory.Facet}
    {first₀ first₁ : StructuralSpan baseCategory A B}
    {second₀ second₁ : StructuralSpan baseCategory B C}
    {third₀ third₁ : StructuralSpan baseCategory C D}
    (alpha : SpanTwoCell first₀ first₁)
    (beta : SpanTwoCell second₀ second₁)
    (gamma : SpanTwoCell third₀ third₁) :
    let firstSecond₀ :=
      selected.select first₀.targetLeg second₀.sourceLeg
    let firstSecond₁ :=
      selected.select first₁.targetLeg second₁.sourceLeg
    let outer₀ :=
      selected.select
        (baseCategory.comp firstSecond₀.snd second₀.targetLeg)
        third₀.sourceLeg
    let outer₁ :=
      selected.select
        (baseCategory.comp firstSecond₁.snd second₁.targetLeg)
        third₁.sourceLeg
    let horizontalInner :=
      SpanTwoCell.horizontal selected alpha beta
    let horizontalOuter :=
      SpanTwoCell.horizontal selected horizontalInner gamma
    baseCategory.comp
        (baseCategory.comp horizontalOuter.arrow outer₁.fst)
        firstSecond₁.snd =
      baseCategory.comp
        (baseCategory.comp outer₀.fst firstSecond₀.snd)
        beta.arrow := by
  dsimp
  calc
    baseCategory.comp
        (baseCategory.comp
          (SpanTwoCell.horizontal
            selected
            (SpanTwoCell.horizontal selected alpha beta)
            gamma).arrow
          (selected.select
            (baseCategory.comp
              (selected.select
                first₁.targetLeg
                second₁.sourceLeg).snd
              second₁.targetLeg)
            third₁.sourceLeg).fst)
        (selected.select first₁.targetLeg second₁.sourceLeg).snd =
        baseCategory.comp
          (baseCategory.comp
            (selected.select
              (baseCategory.comp
                (selected.select
                  first₀.targetLeg
                  second₀.sourceLeg).snd
                second₀.targetLeg)
              third₀.sourceLeg).fst
            (SpanTwoCell.horizontal selected alpha beta).arrow)
          (selected.select first₁.targetLeg second₁.sourceLeg).snd := by
      exact
        congrArg
          (fun arrow =>
            baseCategory.comp
              arrow
              (selected.select
                first₁.targetLeg
                second₁.sourceLeg).snd)
          (SpanTwoCell.horizontal_first_projection
            selected
            (SpanTwoCell.horizontal selected alpha beta)
            gamma)
    _ = baseCategory.comp
          (selected.select
            (baseCategory.comp
              (selected.select
                first₀.targetLeg
                second₀.sourceLeg).snd
              second₀.targetLeg)
            third₀.sourceLeg).fst
          (baseCategory.comp
            (SpanTwoCell.horizontal selected alpha beta).arrow
            (selected.select first₁.targetLeg second₁.sourceLeg).snd) :=
      baseCategory.comp_assoc
        (selected.select
          (baseCategory.comp
            (selected.select
              first₀.targetLeg
              second₀.sourceLeg).snd
            second₀.targetLeg)
          third₀.sourceLeg).fst
        (SpanTwoCell.horizontal selected alpha beta).arrow
        (selected.select first₁.targetLeg second₁.sourceLeg).snd
    _ = baseCategory.comp
          (selected.select
            (baseCategory.comp
              (selected.select
                first₀.targetLeg
                second₀.sourceLeg).snd
              second₀.targetLeg)
            third₀.sourceLeg).fst
          (baseCategory.comp
            (selected.select first₀.targetLeg second₀.sourceLeg).snd
            beta.arrow) := by
      rw [
        SpanTwoCell.horizontal_second_projection
          selected
          alpha
          beta
      ]
    _ = baseCategory.comp
          (baseCategory.comp
            (selected.select
              (baseCategory.comp
                (selected.select
                  first₀.targetLeg
                  second₀.sourceLeg).snd
                second₀.targetLeg)
              third₀.sourceLeg).fst
            (selected.select first₀.targetLeg second₀.sourceLeg).snd)
          beta.arrow := by
      exact
        (baseCategory.comp_assoc
          (selected.select
            (baseCategory.comp
              (selected.select
                first₀.targetLeg
                second₀.sourceLeg).snd
              second₀.targetLeg)
            third₀.sourceLeg).fst
          (selected.select first₀.targetLeg second₀.sourceLeg).snd
          beta.arrow).symm

/-- Third flattened projection of a horizontally composed left-associated
triple. -/
theorem horizontalLeftAssociated_third
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D : baseCategory.Facet}
    {first₀ first₁ : StructuralSpan baseCategory A B}
    {second₀ second₁ : StructuralSpan baseCategory B C}
    {third₀ third₁ : StructuralSpan baseCategory C D}
    (alpha : SpanTwoCell first₀ first₁)
    (beta : SpanTwoCell second₀ second₁)
    (gamma : SpanTwoCell third₀ third₁) :
    let firstSecond₀ :=
      selected.select first₀.targetLeg second₀.sourceLeg
    let firstSecond₁ :=
      selected.select first₁.targetLeg second₁.sourceLeg
    let outer₀ :=
      selected.select
        (baseCategory.comp firstSecond₀.snd second₀.targetLeg)
        third₀.sourceLeg
    let outer₁ :=
      selected.select
        (baseCategory.comp firstSecond₁.snd second₁.targetLeg)
        third₁.sourceLeg
    let horizontalInner :=
      SpanTwoCell.horizontal selected alpha beta
    let horizontalOuter :=
      SpanTwoCell.horizontal selected horizontalInner gamma
    baseCategory.comp horizontalOuter.arrow outer₁.snd =
      baseCategory.comp outer₀.snd gamma.arrow := by
  dsimp
  exact
    SpanTwoCell.horizontal_second_projection
      selected
      (SpanTwoCell.horizontal selected alpha beta)
      gamma

/-- First flattened projection of a horizontally composed right-associated
triple. -/
theorem horizontalRightAssociated_first
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D : baseCategory.Facet}
    {first₀ first₁ : StructuralSpan baseCategory A B}
    {second₀ second₁ : StructuralSpan baseCategory B C}
    {third₀ third₁ : StructuralSpan baseCategory C D}
    (alpha : SpanTwoCell first₀ first₁)
    (beta : SpanTwoCell second₀ second₁)
    (gamma : SpanTwoCell third₀ third₁) :
    let secondThird₀ :=
      selected.select second₀.targetLeg third₀.sourceLeg
    let secondThird₁ :=
      selected.select second₁.targetLeg third₁.sourceLeg
    let outer₀ :=
      selected.select
        first₀.targetLeg
        (baseCategory.comp secondThird₀.fst second₀.sourceLeg)
    let outer₁ :=
      selected.select
        first₁.targetLeg
        (baseCategory.comp secondThird₁.fst second₁.sourceLeg)
    let horizontalInner :=
      SpanTwoCell.horizontal selected beta gamma
    let horizontalOuter :=
      SpanTwoCell.horizontal selected alpha horizontalInner
    baseCategory.comp horizontalOuter.arrow outer₁.fst =
      baseCategory.comp outer₀.fst alpha.arrow := by
  dsimp
  exact
    SpanTwoCell.horizontal_first_projection
      selected
      alpha
      (SpanTwoCell.horizontal selected beta gamma)

/-- Middle flattened projection of a horizontally composed right-associated
triple. -/
theorem horizontalRightAssociated_second
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D : baseCategory.Facet}
    {first₀ first₁ : StructuralSpan baseCategory A B}
    {second₀ second₁ : StructuralSpan baseCategory B C}
    {third₀ third₁ : StructuralSpan baseCategory C D}
    (alpha : SpanTwoCell first₀ first₁)
    (beta : SpanTwoCell second₀ second₁)
    (gamma : SpanTwoCell third₀ third₁) :
    let secondThird₀ :=
      selected.select second₀.targetLeg third₀.sourceLeg
    let secondThird₁ :=
      selected.select second₁.targetLeg third₁.sourceLeg
    let outer₀ :=
      selected.select
        first₀.targetLeg
        (baseCategory.comp secondThird₀.fst second₀.sourceLeg)
    let outer₁ :=
      selected.select
        first₁.targetLeg
        (baseCategory.comp secondThird₁.fst second₁.sourceLeg)
    let horizontalInner :=
      SpanTwoCell.horizontal selected beta gamma
    let horizontalOuter :=
      SpanTwoCell.horizontal selected alpha horizontalInner
    baseCategory.comp
        (baseCategory.comp horizontalOuter.arrow outer₁.snd)
        secondThird₁.fst =
      baseCategory.comp
        (baseCategory.comp outer₀.snd secondThird₀.fst)
        beta.arrow := by
  dsimp
  calc
    baseCategory.comp
        (baseCategory.comp
          (SpanTwoCell.horizontal
            selected
            alpha
            (SpanTwoCell.horizontal selected beta gamma)).arrow
          (selected.select
            first₁.targetLeg
            (baseCategory.comp
              (selected.select
                second₁.targetLeg
                third₁.sourceLeg).fst
              second₁.sourceLeg)).snd)
        (selected.select second₁.targetLeg third₁.sourceLeg).fst =
        baseCategory.comp
          (baseCategory.comp
            (selected.select
              first₀.targetLeg
              (baseCategory.comp
                (selected.select
                  second₀.targetLeg
                  third₀.sourceLeg).fst
                second₀.sourceLeg)).snd
            (SpanTwoCell.horizontal selected beta gamma).arrow)
          (selected.select second₁.targetLeg third₁.sourceLeg).fst := by
      exact
        congrArg
          (fun arrow =>
            baseCategory.comp
              arrow
              (selected.select
                second₁.targetLeg
                third₁.sourceLeg).fst)
          (SpanTwoCell.horizontal_second_projection
            selected
            alpha
            (SpanTwoCell.horizontal selected beta gamma))
    _ = baseCategory.comp
          (selected.select
            first₀.targetLeg
            (baseCategory.comp
              (selected.select
                second₀.targetLeg
                third₀.sourceLeg).fst
              second₀.sourceLeg)).snd
          (baseCategory.comp
            (SpanTwoCell.horizontal selected beta gamma).arrow
            (selected.select second₁.targetLeg third₁.sourceLeg).fst) :=
      baseCategory.comp_assoc
        (selected.select
          first₀.targetLeg
          (baseCategory.comp
            (selected.select
              second₀.targetLeg
              third₀.sourceLeg).fst
            second₀.sourceLeg)).snd
        (SpanTwoCell.horizontal selected beta gamma).arrow
        (selected.select second₁.targetLeg third₁.sourceLeg).fst
    _ = baseCategory.comp
          (selected.select
            first₀.targetLeg
            (baseCategory.comp
              (selected.select
                second₀.targetLeg
                third₀.sourceLeg).fst
              second₀.sourceLeg)).snd
          (baseCategory.comp
            (selected.select second₀.targetLeg third₀.sourceLeg).fst
            beta.arrow) := by
      rw [
        SpanTwoCell.horizontal_first_projection
          selected
          beta
          gamma
      ]
    _ = baseCategory.comp
          (baseCategory.comp
            (selected.select
              first₀.targetLeg
              (baseCategory.comp
                (selected.select
                  second₀.targetLeg
                  third₀.sourceLeg).fst
                second₀.sourceLeg)).snd
            (selected.select second₀.targetLeg third₀.sourceLeg).fst)
          beta.arrow := by
      exact
        (baseCategory.comp_assoc
          (selected.select
            first₀.targetLeg
            (baseCategory.comp
              (selected.select
                second₀.targetLeg
                third₀.sourceLeg).fst
              second₀.sourceLeg)).snd
          (selected.select second₀.targetLeg third₀.sourceLeg).fst
          beta.arrow).symm

/-- Third flattened projection of a horizontally composed right-associated
triple. -/
theorem horizontalRightAssociated_third
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D : baseCategory.Facet}
    {first₀ first₁ : StructuralSpan baseCategory A B}
    {second₀ second₁ : StructuralSpan baseCategory B C}
    {third₀ third₁ : StructuralSpan baseCategory C D}
    (alpha : SpanTwoCell first₀ first₁)
    (beta : SpanTwoCell second₀ second₁)
    (gamma : SpanTwoCell third₀ third₁) :
    let secondThird₀ :=
      selected.select second₀.targetLeg third₀.sourceLeg
    let secondThird₁ :=
      selected.select second₁.targetLeg third₁.sourceLeg
    let outer₀ :=
      selected.select
        first₀.targetLeg
        (baseCategory.comp secondThird₀.fst second₀.sourceLeg)
    let outer₁ :=
      selected.select
        first₁.targetLeg
        (baseCategory.comp secondThird₁.fst second₁.sourceLeg)
    let horizontalInner :=
      SpanTwoCell.horizontal selected beta gamma
    let horizontalOuter :=
      SpanTwoCell.horizontal selected alpha horizontalInner
    baseCategory.comp
        (baseCategory.comp horizontalOuter.arrow outer₁.snd)
        secondThird₁.snd =
      baseCategory.comp
        (baseCategory.comp outer₀.snd secondThird₀.snd)
        gamma.arrow := by
  dsimp
  calc
    baseCategory.comp
        (baseCategory.comp
          (SpanTwoCell.horizontal
            selected
            alpha
            (SpanTwoCell.horizontal selected beta gamma)).arrow
          (selected.select
            first₁.targetLeg
            (baseCategory.comp
              (selected.select
                second₁.targetLeg
                third₁.sourceLeg).fst
              second₁.sourceLeg)).snd)
        (selected.select second₁.targetLeg third₁.sourceLeg).snd =
        baseCategory.comp
          (baseCategory.comp
            (selected.select
              first₀.targetLeg
              (baseCategory.comp
                (selected.select
                  second₀.targetLeg
                  third₀.sourceLeg).fst
                second₀.sourceLeg)).snd
            (SpanTwoCell.horizontal selected beta gamma).arrow)
          (selected.select second₁.targetLeg third₁.sourceLeg).snd := by
      exact
        congrArg
          (fun arrow =>
            baseCategory.comp
              arrow
              (selected.select
                second₁.targetLeg
                third₁.sourceLeg).snd)
          (SpanTwoCell.horizontal_second_projection
            selected
            alpha
            (SpanTwoCell.horizontal selected beta gamma))
    _ = baseCategory.comp
          (selected.select
            first₀.targetLeg
            (baseCategory.comp
              (selected.select
                second₀.targetLeg
                third₀.sourceLeg).fst
              second₀.sourceLeg)).snd
          (baseCategory.comp
            (SpanTwoCell.horizontal selected beta gamma).arrow
            (selected.select second₁.targetLeg third₁.sourceLeg).snd) :=
      baseCategory.comp_assoc
        (selected.select
          first₀.targetLeg
          (baseCategory.comp
            (selected.select
              second₀.targetLeg
              third₀.sourceLeg).fst
            second₀.sourceLeg)).snd
        (SpanTwoCell.horizontal selected beta gamma).arrow
        (selected.select second₁.targetLeg third₁.sourceLeg).snd
    _ = baseCategory.comp
          (selected.select
            first₀.targetLeg
            (baseCategory.comp
              (selected.select
                second₀.targetLeg
                third₀.sourceLeg).fst
              second₀.sourceLeg)).snd
          (baseCategory.comp
            (selected.select second₀.targetLeg third₀.sourceLeg).snd
            gamma.arrow) := by
      rw [
        SpanTwoCell.horizontal_second_projection
          selected
          beta
          gamma
      ]
    _ = baseCategory.comp
          (baseCategory.comp
            (selected.select
              first₀.targetLeg
              (baseCategory.comp
                (selected.select
                  second₀.targetLeg
                  third₀.sourceLeg).fst
                second₀.sourceLeg)).snd
            (selected.select second₀.targetLeg third₀.sourceLeg).snd)
          gamma.arrow := by
      exact
        (baseCategory.comp_assoc
          (selected.select
            first₀.targetLeg
            (baseCategory.comp
              (selected.select
                second₀.targetLeg
                third₀.sourceLeg).fst
              second₀.sourceLeg)).snd
          (selected.select second₀.targetLeg third₀.sourceLeg).snd
          gamma.arrow).symm

/-- Naturality equation for a chosen associator. -/
def SpanAssociatorNaturality
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    {selected : SelectedPullbacks baseCategory}
    (comparisons : SpanComparisonData selected) : Prop :=
  ∀ {A B C D : baseCategory.Facet}
    {first₀ first₁ : StructuralSpan baseCategory A B}
    {second₀ second₁ : StructuralSpan baseCategory B C}
    {third₀ third₁ : StructuralSpan baseCategory C D}
    (alpha : SpanTwoCell first₀ first₁)
    (beta : SpanTwoCell second₀ second₁)
    (gamma : SpanTwoCell third₀ third₁),
    SpanTwoCell.vertical
        (SpanTwoCell.horizontal
          selected
          (SpanTwoCell.horizontal selected alpha beta)
          gamma)
        (comparisons.associator first₁ second₁ third₁).homCell =
      SpanTwoCell.vertical
        (comparisons.associator first₀ second₀ third₀).homCell
        (SpanTwoCell.horizontal
          selected
          alpha
          (SpanTwoCell.horizontal selected beta gamma))

/-- The canonical associator is natural in all three span variables. -/
theorem canonicalAssociator_naturality
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory) :
    SpanAssociatorNaturality
      (canonicalSpanComparisonData selected) := by
  intro A B C D
    first₀ first₁
    second₀ second₁
    third₀ third₁
    alpha beta gamma
  apply SpanTwoCell.ext
  let firstSecond₀ :=
    selected.select first₀.targetLeg second₀.sourceLeg
  let firstSecond₁ :=
    selected.select first₁.targetLeg second₁.sourceLeg
  let secondThird₀ :=
    selected.select second₀.targetLeg third₀.sourceLeg
  let secondThird₁ :=
    selected.select second₁.targetLeg third₁.sourceLeg
  let leftPullback₀ :=
    selected.select
      (baseCategory.comp firstSecond₀.snd second₀.targetLeg)
      third₀.sourceLeg
  let leftPullback₁ :=
    selected.select
      (baseCategory.comp firstSecond₁.snd second₁.targetLeg)
      third₁.sourceLeg
  let rightPullback₀ :=
    selected.select
      first₀.targetLeg
      (baseCategory.comp secondThird₀.fst second₀.sourceLeg)
  let rightPullback₁ :=
    selected.select
      first₁.targetLeg
      (baseCategory.comp secondThird₁.fst second₁.sourceLeg)
  let leftHorizontal :=
    SpanTwoCell.horizontal
      selected
      (SpanTwoCell.horizontal selected alpha beta)
      gamma
  let rightHorizontal :=
    SpanTwoCell.horizontal
      selected
      alpha
      (SpanTwoCell.horizontal selected beta gamma)
  let associator₀ :=
    canonicalAssociator selected first₀ second₀ third₀
  let associator₁ :=
    canonicalAssociator selected first₁ second₁ third₁
  have associator₀First :
      baseCategory.comp associator₀.hom rightPullback₀.fst =
        baseCategory.comp leftPullback₀.fst firstSecond₀.fst :=
    canonicalAssociatorHom_first selected first₀ second₀ third₀
  have associator₀Second :
      baseCategory.comp
          (baseCategory.comp associator₀.hom rightPullback₀.snd)
          secondThird₀.fst =
        baseCategory.comp leftPullback₀.fst firstSecond₀.snd :=
    canonicalAssociatorHom_second selected first₀ second₀ third₀
  have associator₀Third :
      baseCategory.comp
          (baseCategory.comp associator₀.hom rightPullback₀.snd)
          secondThird₀.snd =
        leftPullback₀.snd :=
    canonicalAssociatorHom_third selected first₀ second₀ third₀
  have associator₁First :
      baseCategory.comp associator₁.hom rightPullback₁.fst =
        baseCategory.comp leftPullback₁.fst firstSecond₁.fst :=
    canonicalAssociatorHom_first selected first₁ second₁ third₁
  have associator₁Second :
      baseCategory.comp
          (baseCategory.comp associator₁.hom rightPullback₁.snd)
          secondThird₁.fst =
        baseCategory.comp leftPullback₁.fst firstSecond₁.snd :=
    canonicalAssociatorHom_second selected first₁ second₁ third₁
  have associator₁Third :
      baseCategory.comp
          (baseCategory.comp associator₁.hom rightPullback₁.snd)
          secondThird₁.snd =
        leftPullback₁.snd :=
    canonicalAssociatorHom_third selected first₁ second₁ third₁
  apply
    rightAssociatedTriple_hom_ext
      selected
      first₁
      second₁
      third₁
  · calc
      baseCategory.comp
          (baseCategory.comp leftHorizontal.arrow associator₁.hom)
          rightPullback₁.fst =
          baseCategory.comp
            leftHorizontal.arrow
            (baseCategory.comp associator₁.hom rightPullback₁.fst) :=
        baseCategory.comp_assoc
          leftHorizontal.arrow
          associator₁.hom
          rightPullback₁.fst
      _ = baseCategory.comp
            leftHorizontal.arrow
            (baseCategory.comp leftPullback₁.fst firstSecond₁.fst) := by
        rw [associator₁First]
      _ = baseCategory.comp
            (baseCategory.comp leftHorizontal.arrow leftPullback₁.fst)
            firstSecond₁.fst := by
        exact
          (baseCategory.comp_assoc
            leftHorizontal.arrow
            leftPullback₁.fst
            firstSecond₁.fst).symm
      _ = baseCategory.comp
            (baseCategory.comp leftPullback₀.fst firstSecond₀.fst)
            alpha.arrow :=
        horizontalLeftAssociated_first
          selected
          alpha
          beta
          gamma
      _ = baseCategory.comp
            (baseCategory.comp associator₀.hom rightPullback₀.fst)
            alpha.arrow := by
        rw [associator₀First]
      _ = baseCategory.comp
            associator₀.hom
            (baseCategory.comp rightPullback₀.fst alpha.arrow) :=
        baseCategory.comp_assoc
          associator₀.hom
          rightPullback₀.fst
          alpha.arrow
      _ = baseCategory.comp
            associator₀.hom
            (baseCategory.comp rightHorizontal.arrow rightPullback₁.fst) := by
        rw [
          horizontalRightAssociated_first
            selected
            alpha
            beta
            gamma
        ]
      _ = baseCategory.comp
            (baseCategory.comp associator₀.hom rightHorizontal.arrow)
            rightPullback₁.fst := by
        exact
          (baseCategory.comp_assoc
            associator₀.hom
            rightHorizontal.arrow
            rightPullback₁.fst).symm
  · calc
      baseCategory.comp
          (baseCategory.comp
            (baseCategory.comp leftHorizontal.arrow associator₁.hom)
            rightPullback₁.snd)
          secondThird₁.fst =
          baseCategory.comp
            leftHorizontal.arrow
            (baseCategory.comp
              (baseCategory.comp associator₁.hom rightPullback₁.snd)
              secondThird₁.fst) := by
        exact
          baseCategory.comp_four_middle
            leftHorizontal.arrow
            associator₁.hom
            rightPullback₁.snd
            secondThird₁.fst
      _ = baseCategory.comp
            leftHorizontal.arrow
            (baseCategory.comp leftPullback₁.fst firstSecond₁.snd) := by
        rw [associator₁Second]
      _ = baseCategory.comp
            (baseCategory.comp leftHorizontal.arrow leftPullback₁.fst)
            firstSecond₁.snd := by
        exact
          (baseCategory.comp_assoc
            leftHorizontal.arrow
            leftPullback₁.fst
            firstSecond₁.snd).symm
      _ = baseCategory.comp
            (baseCategory.comp leftPullback₀.fst firstSecond₀.snd)
            beta.arrow :=
        horizontalLeftAssociated_second
          selected
          alpha
          beta
          gamma
      _ = baseCategory.comp
            (baseCategory.comp
              (baseCategory.comp associator₀.hom rightPullback₀.snd)
              secondThird₀.fst)
            beta.arrow := by
        rw [associator₀Second]
      _ = baseCategory.comp
            associator₀.hom
            (baseCategory.comp
              (baseCategory.comp rightPullback₀.snd secondThird₀.fst)
              beta.arrow) := by
        exact
          baseCategory.comp_four_middle
            associator₀.hom
            rightPullback₀.snd
            secondThird₀.fst
            beta.arrow
      _ = baseCategory.comp
            associator₀.hom
            (baseCategory.comp
              (baseCategory.comp rightHorizontal.arrow rightPullback₁.snd)
              secondThird₁.fst) := by
        rw [
          horizontalRightAssociated_second
            selected
            alpha
            beta
            gamma
        ]
      _ = baseCategory.comp
            (baseCategory.comp
              (baseCategory.comp associator₀.hom rightHorizontal.arrow)
              rightPullback₁.snd)
            secondThird₁.fst := by
        exact
          (baseCategory.comp_four_middle
            associator₀.hom
            rightHorizontal.arrow
            rightPullback₁.snd
            secondThird₁.fst).symm
  · calc
      baseCategory.comp
          (baseCategory.comp
            (baseCategory.comp leftHorizontal.arrow associator₁.hom)
            rightPullback₁.snd)
          secondThird₁.snd =
          baseCategory.comp
            leftHorizontal.arrow
            (baseCategory.comp
              (baseCategory.comp associator₁.hom rightPullback₁.snd)
              secondThird₁.snd) := by
        exact
          baseCategory.comp_four_middle
            leftHorizontal.arrow
            associator₁.hom
            rightPullback₁.snd
            secondThird₁.snd
      _ = baseCategory.comp leftHorizontal.arrow leftPullback₁.snd := by
        rw [associator₁Third]
      _ = baseCategory.comp leftPullback₀.snd gamma.arrow :=
        horizontalLeftAssociated_third
          selected
          alpha
          beta
          gamma
      _ = baseCategory.comp
            (baseCategory.comp
              (baseCategory.comp associator₀.hom rightPullback₀.snd)
              secondThird₀.snd)
            gamma.arrow := by
        rw [associator₀Third]
      _ = baseCategory.comp
            associator₀.hom
            (baseCategory.comp
              (baseCategory.comp rightPullback₀.snd secondThird₀.snd)
              gamma.arrow) := by
        exact
          baseCategory.comp_four_middle
            associator₀.hom
            rightPullback₀.snd
            secondThird₀.snd
            gamma.arrow
      _ = baseCategory.comp
            associator₀.hom
            (baseCategory.comp
              (baseCategory.comp rightHorizontal.arrow rightPullback₁.snd)
              secondThird₁.snd) := by
        rw [
          horizontalRightAssociated_third
            selected
            alpha
            beta
            gamma
        ]
      _ = baseCategory.comp
            (baseCategory.comp
              (baseCategory.comp associator₀.hom rightHorizontal.arrow)
              rightPullback₁.snd)
            secondThird₁.snd := by
        exact
          (baseCategory.comp_four_middle
            associator₀.hom
            rightHorizontal.arrow
            rightPullback₁.snd
            secondThird₁.snd).symm

/-- The forward map of the canonical left unitor is the second pullback
projection. -/
theorem canonicalLeftUnitor_hom
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B : baseCategory.Facet}
    (span : StructuralSpan baseCategory A B) :
    (canonicalLeftUnitor selected span).hom =
      (selected.select (baseCategory.id A) span.sourceLeg).snd :=
  rfl

/-- The forward map of the canonical right unitor is the first pullback
projection. -/
theorem canonicalRightUnitor_hom
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B : baseCategory.Facet}
    (span : StructuralSpan baseCategory A B) :
    (canonicalRightUnitor selected span).hom =
      (selected.select span.targetLeg (baseCategory.id B)).fst :=
  rfl

/-- The canonical comparisons satisfy the triangle equation. -/
theorem canonicalSpanTriangle
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory) :
    SpanTriangleEquation
      (canonicalSpanComparisonData selected) := by
  intro A B C first second
  apply SpanTwoCell.ext
  let firstIdentity :=
    selected.select first.targetLeg (baseCategory.id B)
  let identitySecond :=
    selected.select (baseCategory.id B) second.sourceLeg
  let sourcePullback :=
    selected.select
      (baseCategory.comp firstIdentity.snd (baseCategory.id B))
      second.sourceLeg
  let rightAssociated :=
    selected.select
      first.targetLeg
      (baseCategory.comp identitySecond.fst (baseCategory.id B))
  let targetPullback :=
    selected.select first.targetLeg second.sourceLeg
  let associator :=
    canonicalAssociator
      selected
      first
      (StructuralSpan.identity B)
      second
  let leftUnitor :=
    canonicalLeftUnitor selected second
  let rightUnitor :=
    canonicalRightUnitor selected first
  let leftWhisker :=
    SpanTwoCell.horizontal
      selected
      (SpanTwoCell.identity first)
      leftUnitor.homCell
  let rightWhisker :=
    SpanTwoCell.horizontal
      selected
      rightUnitor.homCell
      (SpanTwoCell.identity second)
  have associatorFirst :
      baseCategory.comp associator.hom rightAssociated.fst =
        baseCategory.comp sourcePullback.fst firstIdentity.fst :=
    canonicalAssociatorHom_first
      selected
      first
      (StructuralSpan.identity B)
      second
  have associatorThird :
      baseCategory.comp
          (baseCategory.comp associator.hom rightAssociated.snd)
          identitySecond.snd =
        sourcePullback.snd :=
    canonicalAssociatorHom_third
      selected
      first
      (StructuralSpan.identity B)
      second
  have leftWhiskerFirst :
      baseCategory.comp leftWhisker.arrow targetPullback.fst =
        baseCategory.comp
          rightAssociated.fst
          (baseCategory.id first.apex) :=
    SpanTwoCell.horizontal_first_projection
      selected
      (SpanTwoCell.identity first)
      leftUnitor.homCell
  have leftWhiskerSecond :
      baseCategory.comp leftWhisker.arrow targetPullback.snd =
        baseCategory.comp rightAssociated.snd identitySecond.snd := by
    simpa [leftUnitor, identitySecond] using
      (SpanTwoCell.horizontal_second_projection
        selected
        (SpanTwoCell.identity first)
        leftUnitor.homCell)
  have rightWhiskerFirst :
      baseCategory.comp rightWhisker.arrow targetPullback.fst =
        baseCategory.comp sourcePullback.fst firstIdentity.fst := by
    simpa [rightUnitor, firstIdentity] using
      (SpanTwoCell.horizontal_first_projection
        selected
        rightUnitor.homCell
        (SpanTwoCell.identity second))
  have rightWhiskerSecond :
      baseCategory.comp rightWhisker.arrow targetPullback.snd =
        baseCategory.comp
          sourcePullback.snd
          (baseCategory.id second.apex) :=
    SpanTwoCell.horizontal_second_projection
      selected
      rightUnitor.homCell
      (SpanTwoCell.identity second)
  apply targetPullback.hom_ext
  · calc
      baseCategory.comp
          (baseCategory.comp associator.hom leftWhisker.arrow)
          targetPullback.fst =
          baseCategory.comp
            associator.hom
            (baseCategory.comp leftWhisker.arrow targetPullback.fst) :=
        baseCategory.comp_assoc
          associator.hom
          leftWhisker.arrow
          targetPullback.fst
      _ = baseCategory.comp
            associator.hom
            (baseCategory.comp
              rightAssociated.fst
              (baseCategory.id first.apex)) := by
        rw [leftWhiskerFirst]
      _ = baseCategory.comp associator.hom rightAssociated.fst := by
        rw [baseCategory.comp_id]
      _ = baseCategory.comp sourcePullback.fst firstIdentity.fst :=
        associatorFirst
      _ = baseCategory.comp rightWhisker.arrow targetPullback.fst :=
        rightWhiskerFirst.symm
  · calc
      baseCategory.comp
          (baseCategory.comp associator.hom leftWhisker.arrow)
          targetPullback.snd =
          baseCategory.comp
            associator.hom
            (baseCategory.comp leftWhisker.arrow targetPullback.snd) :=
        baseCategory.comp_assoc
          associator.hom
          leftWhisker.arrow
          targetPullback.snd
      _ = baseCategory.comp
            associator.hom
            (baseCategory.comp rightAssociated.snd identitySecond.snd) := by
        rw [leftWhiskerSecond]
      _ = baseCategory.comp
            (baseCategory.comp associator.hom rightAssociated.snd)
            identitySecond.snd := by
        exact
          (baseCategory.comp_assoc
            associator.hom
            rightAssociated.snd
            identitySecond.snd).symm
      _ = sourcePullback.snd :=
        associatorThird
      _ = baseCategory.comp
            sourcePullback.snd
            (baseCategory.id second.apex) := by
        exact (baseCategory.comp_id sourcePullback.snd).symm
      _ = baseCategory.comp rightWhisker.arrow targetPullback.snd :=
        rightWhiskerSecond.symm

/-- Extensionality for arrows into the fully right-associated fourfold
composite. It is obtained by applying the selected outer pullback
extensionality and then the already derived right-associated triple
extensionality; no new coherence principle is assumed. -/
theorem rightAssociatedFour_hom_ext
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D E : baseCategory.Facet}
    (first : StructuralSpan baseCategory A B)
    (second : StructuralSpan baseCategory B C)
    (third : StructuralSpan baseCategory C D)
    (fourth : StructuralSpan baseCategory D E)
    {Q : baseCategory.Facet}
    (left right :
      baseCategory.Hom
        Q
        (StructuralSpan.compose
          selected
          first
          (StructuralSpan.compose
            selected
            second
            (StructuralSpan.compose selected third fourth))).apex)
    (firstProjection :
      let thirdFourth :=
        selected.select third.targetLeg fourth.sourceLeg
      let secondRest :=
        selected.select
          second.targetLeg
          (baseCategory.comp thirdFourth.fst third.sourceLeg)
      let outer :=
        selected.select
          first.targetLeg
          (baseCategory.comp secondRest.fst second.sourceLeg)
      baseCategory.comp left outer.fst =
        baseCategory.comp right outer.fst)
    (secondProjection :
      let thirdFourth :=
        selected.select third.targetLeg fourth.sourceLeg
      let secondRest :=
        selected.select
          second.targetLeg
          (baseCategory.comp thirdFourth.fst third.sourceLeg)
      let outer :=
        selected.select
          first.targetLeg
          (baseCategory.comp secondRest.fst second.sourceLeg)
      baseCategory.comp
          (baseCategory.comp left outer.snd)
          secondRest.fst =
        baseCategory.comp
          (baseCategory.comp right outer.snd)
          secondRest.fst)
    (thirdProjection :
      let thirdFourth :=
        selected.select third.targetLeg fourth.sourceLeg
      let secondRest :=
        selected.select
          second.targetLeg
          (baseCategory.comp thirdFourth.fst third.sourceLeg)
      let outer :=
        selected.select
          first.targetLeg
          (baseCategory.comp secondRest.fst second.sourceLeg)
      baseCategory.comp
          (baseCategory.comp
            (baseCategory.comp left outer.snd)
            secondRest.snd)
          thirdFourth.fst =
        baseCategory.comp
          (baseCategory.comp
            (baseCategory.comp right outer.snd)
            secondRest.snd)
          thirdFourth.fst)
    (fourthProjection :
      let thirdFourth :=
        selected.select third.targetLeg fourth.sourceLeg
      let secondRest :=
        selected.select
          second.targetLeg
          (baseCategory.comp thirdFourth.fst third.sourceLeg)
      let outer :=
        selected.select
          first.targetLeg
          (baseCategory.comp secondRest.fst second.sourceLeg)
      baseCategory.comp
          (baseCategory.comp
            (baseCategory.comp left outer.snd)
            secondRest.snd)
          thirdFourth.snd =
        baseCategory.comp
          (baseCategory.comp
            (baseCategory.comp right outer.snd)
            secondRest.snd)
          thirdFourth.snd) :
    left = right := by
  let thirdFourth :=
    selected.select third.targetLeg fourth.sourceLeg
  let secondRest :=
    selected.select
      second.targetLeg
      (baseCategory.comp thirdFourth.fst third.sourceLeg)
  let outer :=
    selected.select
      first.targetLeg
      (baseCategory.comp secondRest.fst second.sourceLeg)
  apply outer.hom_ext
  · exact firstProjection
  · apply
      rightAssociatedTriple_hom_ext
        selected
        second
        third
        fourth
    · exact secondProjection
    · exact thirdProjection
    · exact fourthProjection

/-- The two-associator route around the left side of the pentagon. -/
def canonicalPentagonLeftPath
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D E : baseCategory.Facet}
    (first : StructuralSpan baseCategory A B)
    (second : StructuralSpan baseCategory B C)
    (third : StructuralSpan baseCategory C D)
    (fourth : StructuralSpan baseCategory D E) :
    SpanTwoCell
      (StructuralSpan.compose
        selected
        (StructuralSpan.compose
          selected
          (StructuralSpan.compose selected first second)
          third)
        fourth)
      (StructuralSpan.compose
        selected
        first
        (StructuralSpan.compose
          selected
          second
          (StructuralSpan.compose selected third fourth))) :=
  SpanTwoCell.vertical
    (canonicalAssociator
      selected
      (StructuralSpan.compose selected first second)
      third
      fourth).homCell
    (canonicalAssociator
      selected
      first
      second
      (StructuralSpan.compose selected third fourth)).homCell

/-- The whisker-associator-whisker route around the right side of the
pentagon. -/
def canonicalPentagonRightPath
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D E : baseCategory.Facet}
    (first : StructuralSpan baseCategory A B)
    (second : StructuralSpan baseCategory B C)
    (third : StructuralSpan baseCategory C D)
    (fourth : StructuralSpan baseCategory D E) :
    SpanTwoCell
      (StructuralSpan.compose
        selected
        (StructuralSpan.compose
          selected
          (StructuralSpan.compose selected first second)
          third)
        fourth)
      (StructuralSpan.compose
        selected
        first
        (StructuralSpan.compose
          selected
          second
          (StructuralSpan.compose selected third fourth))) :=
  SpanTwoCell.vertical
    (SpanTwoCell.horizontal
      selected
      (canonicalAssociator selected first second third).homCell
      (SpanTwoCell.identity fourth))
    (SpanTwoCell.vertical
      (canonicalAssociator
        selected
        first
        (StructuralSpan.compose selected second third)
        fourth).homCell
      (SpanTwoCell.horizontal
        selected
        (SpanTwoCell.identity first)
        (canonicalAssociator selected second third fourth).homCell))

/-- Both canonical pentagon paths have the same flattened projection to the
first constituent span. -/
theorem canonicalPentagon_first_projection
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D E : baseCategory.Facet}
    (first : StructuralSpan baseCategory A B)
    (second : StructuralSpan baseCategory B C)
    (third : StructuralSpan baseCategory C D)
    (fourth : StructuralSpan baseCategory D E) :
    let thirdFourth :=
      selected.select third.targetLeg fourth.sourceLeg
    let secondRest :=
      selected.select
        second.targetLeg
        (baseCategory.comp thirdFourth.fst third.sourceLeg)
    let targetOuter :=
      selected.select
        first.targetLeg
        (baseCategory.comp secondRest.fst second.sourceLeg)
    baseCategory.comp
        (canonicalPentagonLeftPath
          selected first second third fourth).arrow
        targetOuter.fst =
      baseCategory.comp
        (canonicalPentagonRightPath
          selected first second third fourth).arrow
        targetOuter.fst := by
  dsimp only
  let firstSecond :=
    selected.select first.targetLeg second.sourceLeg
  let secondThird :=
    selected.select second.targetLeg third.sourceLeg
  let thirdFourth :=
    selected.select third.targetLeg fourth.sourceLeg
  let sourceTriple :=
    selected.select
      (baseCategory.comp firstSecond.snd second.targetLeg)
      third.sourceLeg
  let sourceOuter :=
    selected.select
      (baseCategory.comp sourceTriple.snd third.targetLeg)
      fourth.sourceLeg
  let leftMiddle :=
    selected.select
      (baseCategory.comp firstSecond.snd second.targetLeg)
      (baseCategory.comp thirdFourth.fst third.sourceLeg)
  let rightFirstTriple :=
    selected.select
      first.targetLeg
      (baseCategory.comp secondThird.fst second.sourceLeg)
  let rightMiddleOne :=
    selected.select
      (baseCategory.comp
        rightFirstTriple.snd
        (baseCategory.comp secondThird.snd third.targetLeg))
      fourth.sourceLeg
  let leftSecondTriple :=
    selected.select
      (baseCategory.comp secondThird.snd third.targetLeg)
      fourth.sourceLeg
  let rightMiddleTwo :=
    selected.select
      first.targetLeg
      (baseCategory.comp
        leftSecondTriple.fst
        (baseCategory.comp secondThird.fst second.sourceLeg))
  let rightSecondTriple :=
    selected.select
      second.targetLeg
      (baseCategory.comp thirdFourth.fst third.sourceLeg)
  let targetOuter :=
    selected.select
      first.targetLeg
      (baseCategory.comp rightSecondTriple.fst second.sourceLeg)
  let leftOuterAssociator :=
    canonicalAssociator
      selected
      (StructuralSpan.compose selected first second)
      third
      fourth
  let leftInnerAssociator :=
    canonicalAssociator
      selected
      first
      second
      (StructuralSpan.compose selected third fourth)
  let firstAssociator :=
    canonicalAssociator selected first second third
  let firstWhisker :=
    SpanTwoCell.horizontal
      selected
      firstAssociator.homCell
      (SpanTwoCell.identity fourth)
  let middleAssociator :=
    canonicalAssociator
      selected
      first
      (StructuralSpan.compose selected second third)
      fourth
  let lastAssociator :=
    canonicalAssociator selected second third fourth
  let lastWhisker :=
    SpanTwoCell.horizontal
      selected
      (SpanTwoCell.identity first)
      lastAssociator.homCell
  have leftInnerFirst :
      baseCategory.comp leftInnerAssociator.hom targetOuter.fst =
        baseCategory.comp leftMiddle.fst firstSecond.fst :=
    canonicalAssociatorHom_first
      selected
      first
      second
      (StructuralSpan.compose selected third fourth)
  have leftOuterFirst :
      baseCategory.comp leftOuterAssociator.hom leftMiddle.fst =
        baseCategory.comp sourceOuter.fst sourceTriple.fst :=
    canonicalAssociatorHom_first
      selected
      (StructuralSpan.compose selected first second)
      third
      fourth
  have lastWhiskerFirst :
      baseCategory.comp lastWhisker.arrow targetOuter.fst =
        baseCategory.comp
          rightMiddleTwo.fst
          (baseCategory.id first.apex) :=
    SpanTwoCell.horizontal_first_projection
      selected
      (SpanTwoCell.identity first)
      lastAssociator.homCell
  have middleFirst :
      baseCategory.comp middleAssociator.hom rightMiddleTwo.fst =
        baseCategory.comp rightMiddleOne.fst rightFirstTriple.fst :=
    canonicalAssociatorHom_first
      selected
      first
      (StructuralSpan.compose selected second third)
      fourth
  have firstWhiskerFirst :
      baseCategory.comp firstWhisker.arrow rightMiddleOne.fst =
        baseCategory.comp sourceOuter.fst firstAssociator.hom :=
    SpanTwoCell.horizontal_first_projection
      selected
      firstAssociator.homCell
      (SpanTwoCell.identity fourth)
  have firstAssociatorFirst :
      baseCategory.comp firstAssociator.hom rightFirstTriple.fst =
        baseCategory.comp sourceTriple.fst firstSecond.fst :=
    canonicalAssociatorHom_first
      selected
      first
      second
      third
  calc
    baseCategory.comp
        (canonicalPentagonLeftPath
          selected first second third fourth).arrow
        targetOuter.fst =
        baseCategory.comp
          leftOuterAssociator.hom
          (baseCategory.comp leftInnerAssociator.hom targetOuter.fst) :=
      baseCategory.comp_assoc
        leftOuterAssociator.hom
        leftInnerAssociator.hom
        targetOuter.fst
    _ = baseCategory.comp
          leftOuterAssociator.hom
          (baseCategory.comp leftMiddle.fst firstSecond.fst) := by
      rw [leftInnerFirst]
    _ = baseCategory.comp
          (baseCategory.comp leftOuterAssociator.hom leftMiddle.fst)
          firstSecond.fst := by
      exact
        (baseCategory.comp_assoc
          leftOuterAssociator.hom
          leftMiddle.fst
          firstSecond.fst).symm
    _ = baseCategory.comp
          (baseCategory.comp sourceOuter.fst sourceTriple.fst)
          firstSecond.fst := by
      rw [leftOuterFirst]
    _ = baseCategory.comp
          sourceOuter.fst
          (baseCategory.comp sourceTriple.fst firstSecond.fst) :=
      baseCategory.comp_assoc
        sourceOuter.fst
        sourceTriple.fst
        firstSecond.fst
    _ = baseCategory.comp
          sourceOuter.fst
          (baseCategory.comp firstAssociator.hom rightFirstTriple.fst) := by
      rw [firstAssociatorFirst]
    _ = baseCategory.comp
          (baseCategory.comp sourceOuter.fst firstAssociator.hom)
          rightFirstTriple.fst := by
      exact
        (baseCategory.comp_assoc
          sourceOuter.fst
          firstAssociator.hom
          rightFirstTriple.fst).symm
    _ = baseCategory.comp
          (baseCategory.comp firstWhisker.arrow rightMiddleOne.fst)
          rightFirstTriple.fst := by
      rw [firstWhiskerFirst]
    _ = baseCategory.comp
          firstWhisker.arrow
          (baseCategory.comp rightMiddleOne.fst rightFirstTriple.fst) :=
      baseCategory.comp_assoc
        firstWhisker.arrow
        rightMiddleOne.fst
        rightFirstTriple.fst
    _ = baseCategory.comp
          firstWhisker.arrow
          (baseCategory.comp middleAssociator.hom rightMiddleTwo.fst) := by
      rw [middleFirst]
    _ = baseCategory.comp
          (baseCategory.comp firstWhisker.arrow middleAssociator.hom)
          rightMiddleTwo.fst := by
      exact
        (baseCategory.comp_assoc
          firstWhisker.arrow
          middleAssociator.hom
          rightMiddleTwo.fst).symm
    _ = baseCategory.comp
          (baseCategory.comp firstWhisker.arrow middleAssociator.hom)
          (baseCategory.comp
            lastWhisker.arrow
            targetOuter.fst) := by
      rw [lastWhiskerFirst, baseCategory.comp_id]
    _ = baseCategory.comp
          (baseCategory.comp
            firstWhisker.arrow
            (baseCategory.comp middleAssociator.hom lastWhisker.arrow))
          targetOuter.fst := by
      calc
        baseCategory.comp
            (baseCategory.comp firstWhisker.arrow middleAssociator.hom)
            (baseCategory.comp lastWhisker.arrow targetOuter.fst) =
            baseCategory.comp
              firstWhisker.arrow
              (baseCategory.comp
                middleAssociator.hom
                (baseCategory.comp lastWhisker.arrow targetOuter.fst)) :=
          baseCategory.comp_assoc
            firstWhisker.arrow
            middleAssociator.hom
            (baseCategory.comp lastWhisker.arrow targetOuter.fst)
        _ = baseCategory.comp
              firstWhisker.arrow
              (baseCategory.comp
                (baseCategory.comp middleAssociator.hom lastWhisker.arrow)
                targetOuter.fst) := by
          rw [
            baseCategory.comp_assoc
              middleAssociator.hom
              lastWhisker.arrow
              targetOuter.fst
          ]
        _ = baseCategory.comp
              (baseCategory.comp
                firstWhisker.arrow
                (baseCategory.comp middleAssociator.hom lastWhisker.arrow))
              targetOuter.fst := by
          exact
            (baseCategory.comp_assoc
              firstWhisker.arrow
              (baseCategory.comp
                middleAssociator.hom
                lastWhisker.arrow)
              targetOuter.fst).symm
    _ = baseCategory.comp
          (canonicalPentagonRightPath
            selected first second third fourth).arrow
          targetOuter.fst :=
      rfl

/-- Both canonical pentagon paths have the same flattened projection to the
second constituent span. -/
theorem canonicalPentagon_second_projection
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D E : baseCategory.Facet}
    (first : StructuralSpan baseCategory A B)
    (second : StructuralSpan baseCategory B C)
    (third : StructuralSpan baseCategory C D)
    (fourth : StructuralSpan baseCategory D E) :
    let thirdFourth :=
      selected.select third.targetLeg fourth.sourceLeg
    let secondRest :=
      selected.select
        second.targetLeg
        (baseCategory.comp thirdFourth.fst third.sourceLeg)
    let targetOuter :=
      selected.select
        first.targetLeg
        (baseCategory.comp secondRest.fst second.sourceLeg)
    baseCategory.comp
        (baseCategory.comp
          (canonicalPentagonLeftPath
            selected first second third fourth).arrow
          targetOuter.snd)
        secondRest.fst =
      baseCategory.comp
        (baseCategory.comp
          (canonicalPentagonRightPath
            selected first second third fourth).arrow
          targetOuter.snd)
        secondRest.fst := by
  dsimp only
  let firstSecond :=
    selected.select first.targetLeg second.sourceLeg
  let secondThird :=
    selected.select second.targetLeg third.sourceLeg
  let thirdFourth :=
    selected.select third.targetLeg fourth.sourceLeg
  let sourceTriple :=
    selected.select
      (baseCategory.comp firstSecond.snd second.targetLeg)
      third.sourceLeg
  let sourceOuter :=
    selected.select
      (baseCategory.comp sourceTriple.snd third.targetLeg)
      fourth.sourceLeg
  let leftMiddle :=
    selected.select
      (baseCategory.comp firstSecond.snd second.targetLeg)
      (baseCategory.comp thirdFourth.fst third.sourceLeg)
  let rightFirstTriple :=
    selected.select
      first.targetLeg
      (baseCategory.comp secondThird.fst second.sourceLeg)
  let rightMiddleOne :=
    selected.select
      (baseCategory.comp
        rightFirstTriple.snd
        (baseCategory.comp secondThird.snd third.targetLeg))
      fourth.sourceLeg
  let leftSecondTriple :=
    selected.select
      (baseCategory.comp secondThird.snd third.targetLeg)
      fourth.sourceLeg
  let rightMiddleTwo :=
    selected.select
      first.targetLeg
      (baseCategory.comp
        leftSecondTriple.fst
        (baseCategory.comp secondThird.fst second.sourceLeg))
  let rightSecondTriple :=
    selected.select
      second.targetLeg
      (baseCategory.comp thirdFourth.fst third.sourceLeg)
  let targetOuter :=
    selected.select
      first.targetLeg
      (baseCategory.comp rightSecondTriple.fst second.sourceLeg)
  let leftOuterAssociator :=
    canonicalAssociator
      selected
      (StructuralSpan.compose selected first second)
      third
      fourth
  let leftInnerAssociator :=
    canonicalAssociator
      selected
      first
      second
      (StructuralSpan.compose selected third fourth)
  let firstAssociator :=
    canonicalAssociator selected first second third
  let firstWhisker :=
    SpanTwoCell.horizontal
      selected
      firstAssociator.homCell
      (SpanTwoCell.identity fourth)
  let middleAssociator :=
    canonicalAssociator
      selected
      first
      (StructuralSpan.compose selected second third)
      fourth
  let lastAssociator :=
    canonicalAssociator selected second third fourth
  let lastWhisker :=
    SpanTwoCell.horizontal
      selected
      (SpanTwoCell.identity first)
      lastAssociator.homCell
  have leftInnerSecond :
      baseCategory.comp
          (baseCategory.comp
            leftInnerAssociator.hom
            targetOuter.snd)
          rightSecondTriple.fst =
        baseCategory.comp leftMiddle.fst firstSecond.snd :=
    canonicalAssociatorHom_second
      selected
      first
      second
      (StructuralSpan.compose selected third fourth)
  have leftOuterFirst :
      baseCategory.comp leftOuterAssociator.hom leftMiddle.fst =
        baseCategory.comp sourceOuter.fst sourceTriple.fst :=
    canonicalAssociatorHom_first
      selected
      (StructuralSpan.compose selected first second)
      third
      fourth
  have firstAssociatorSecond :
      baseCategory.comp
          (baseCategory.comp firstAssociator.hom rightFirstTriple.snd)
          secondThird.fst =
        baseCategory.comp sourceTriple.fst firstSecond.snd :=
    canonicalAssociatorHom_second
      selected
      first
      second
      third
  have firstWhiskerFirst :
      baseCategory.comp firstWhisker.arrow rightMiddleOne.fst =
        baseCategory.comp sourceOuter.fst firstAssociator.hom :=
    SpanTwoCell.horizontal_first_projection
      selected
      firstAssociator.homCell
      (SpanTwoCell.identity fourth)
  have middleSecond :
      baseCategory.comp
          (baseCategory.comp middleAssociator.hom rightMiddleTwo.snd)
          leftSecondTriple.fst =
        baseCategory.comp rightMiddleOne.fst rightFirstTriple.snd :=
    canonicalAssociatorHom_second
      selected
      first
      (StructuralSpan.compose selected second third)
      fourth
  have lastAssociatorFirst :
      baseCategory.comp lastAssociator.hom rightSecondTriple.fst =
        baseCategory.comp leftSecondTriple.fst secondThird.fst :=
    canonicalAssociatorHom_first
      selected
      second
      third
      fourth
  have lastWhiskerSecond :
      baseCategory.comp lastWhisker.arrow targetOuter.snd =
        baseCategory.comp rightMiddleTwo.snd lastAssociator.hom :=
    SpanTwoCell.horizontal_second_projection
      selected
      (SpanTwoCell.identity first)
      lastAssociator.homCell
  have rightPathArrow :
      (canonicalPentagonRightPath
        selected first second third fourth).arrow =
        baseCategory.comp
          firstWhisker.arrow
          (baseCategory.comp middleAssociator.hom lastWhisker.arrow) := by
    dsimp [
      canonicalPentagonRightPath,
      SpanTwoCell.vertical,
      SpanIsomorphism.homCell,
      firstWhisker,
      middleAssociator,
      lastWhisker
    ]
  have leftPathArrow :
      (canonicalPentagonLeftPath
        selected first second third fourth).arrow =
        baseCategory.comp
          leftOuterAssociator.hom
          leftInnerAssociator.hom := by
    dsimp [
      canonicalPentagonLeftPath,
      SpanTwoCell.vertical,
      SpanIsomorphism.homCell,
      leftOuterAssociator,
      leftInnerAssociator
    ]
  trans
    baseCategory.comp
      sourceOuter.fst
      (baseCategory.comp sourceTriple.fst firstSecond.snd)
  · calc
      baseCategory.comp
          (baseCategory.comp
            (canonicalPentagonLeftPath
              selected first second third fourth).arrow
            targetOuter.snd)
          rightSecondTriple.fst =
          baseCategory.comp
            leftOuterAssociator.hom
            (baseCategory.comp
              (baseCategory.comp
                leftInnerAssociator.hom
                targetOuter.snd)
              rightSecondTriple.fst) :=
        baseCategory.comp_four_middle
          leftOuterAssociator.hom
          leftInnerAssociator.hom
          targetOuter.snd
          rightSecondTriple.fst
      _ = baseCategory.comp
            leftOuterAssociator.hom
            (baseCategory.comp leftMiddle.fst firstSecond.snd) := by
        rw [leftInnerSecond]
      _ = baseCategory.comp
            (baseCategory.comp leftOuterAssociator.hom leftMiddle.fst)
            firstSecond.snd := by
        exact
          (baseCategory.comp_assoc
            leftOuterAssociator.hom
            leftMiddle.fst
            firstSecond.snd).symm
      _ = baseCategory.comp
            (baseCategory.comp sourceOuter.fst sourceTriple.fst)
            firstSecond.snd := by
        rw [leftOuterFirst]
      _ = baseCategory.comp
            sourceOuter.fst
            (baseCategory.comp sourceTriple.fst firstSecond.snd) :=
        baseCategory.comp_assoc
          sourceOuter.fst
          sourceTriple.fst
          firstSecond.snd
  · symm
    calc
      baseCategory.comp
          (baseCategory.comp
            (canonicalPentagonRightPath
              selected first second third fourth).arrow
            targetOuter.snd)
          rightSecondTriple.fst =
          baseCategory.comp
            firstWhisker.arrow
            (baseCategory.comp
              middleAssociator.hom
              (baseCategory.comp
                (baseCategory.comp lastWhisker.arrow targetOuter.snd)
                rightSecondTriple.fst)) := by
        calc
          baseCategory.comp
              (baseCategory.comp
                (canonicalPentagonRightPath
                  selected first second third fourth).arrow
                targetOuter.snd)
              rightSecondTriple.fst =
              baseCategory.comp
                (canonicalPentagonRightPath
                  selected first second third fourth).arrow
                (baseCategory.comp
                  targetOuter.snd
                  rightSecondTriple.fst) :=
            baseCategory.comp_assoc
              (canonicalPentagonRightPath
                selected first second third fourth).arrow
              targetOuter.snd
              rightSecondTriple.fst
          _ = baseCategory.comp
                firstWhisker.arrow
                (baseCategory.comp
                  (baseCategory.comp middleAssociator.hom lastWhisker.arrow)
                  (baseCategory.comp
                    targetOuter.snd
                    rightSecondTriple.fst)) := by
            rw [rightPathArrow]
            exact
              baseCategory.comp_assoc
                firstWhisker.arrow
                (baseCategory.comp
                  middleAssociator.hom
                  lastWhisker.arrow)
                (baseCategory.comp
                  targetOuter.snd
                  rightSecondTriple.fst)
          _ = baseCategory.comp
                firstWhisker.arrow
                (baseCategory.comp
                  middleAssociator.hom
                  (baseCategory.comp
                    lastWhisker.arrow
                    (baseCategory.comp
                      targetOuter.snd
                      rightSecondTriple.fst))) := by
            rw [
              baseCategory.comp_assoc
                middleAssociator.hom
                lastWhisker.arrow
                (baseCategory.comp
                  targetOuter.snd
                  rightSecondTriple.fst)
            ]
          _ = baseCategory.comp
                firstWhisker.arrow
                (baseCategory.comp
                  middleAssociator.hom
                  (baseCategory.comp
                    (baseCategory.comp lastWhisker.arrow targetOuter.snd)
                    rightSecondTriple.fst)) := by
            rw [
              baseCategory.comp_assoc
                lastWhisker.arrow
                targetOuter.snd
                rightSecondTriple.fst
            ]
      _ = baseCategory.comp
            firstWhisker.arrow
            (baseCategory.comp
              middleAssociator.hom
              (baseCategory.comp
                (baseCategory.comp
                  rightMiddleTwo.snd
                  lastAssociator.hom)
                rightSecondTriple.fst)) := by
        rw [lastWhiskerSecond]
      _ = baseCategory.comp
            firstWhisker.arrow
            (baseCategory.comp
              middleAssociator.hom
              (baseCategory.comp
                rightMiddleTwo.snd
                (baseCategory.comp
                  lastAssociator.hom
                  rightSecondTriple.fst))) := by
        rw [
          baseCategory.comp_assoc
            rightMiddleTwo.snd
            lastAssociator.hom
            rightSecondTriple.fst
        ]
      _ = baseCategory.comp
            firstWhisker.arrow
            (baseCategory.comp
              middleAssociator.hom
              (baseCategory.comp
                rightMiddleTwo.snd
                (baseCategory.comp
                  leftSecondTriple.fst
                  secondThird.fst))) := by
        rw [lastAssociatorFirst]
      _ = baseCategory.comp
            firstWhisker.arrow
            (baseCategory.comp
              (baseCategory.comp
                (baseCategory.comp
                  middleAssociator.hom
                  rightMiddleTwo.snd)
                leftSecondTriple.fst)
              secondThird.fst) := by
        calc
          baseCategory.comp
              firstWhisker.arrow
              (baseCategory.comp
                middleAssociator.hom
                (baseCategory.comp
                  rightMiddleTwo.snd
                  (baseCategory.comp
                    leftSecondTriple.fst
                    secondThird.fst))) =
              baseCategory.comp
                firstWhisker.arrow
                (baseCategory.comp
                  (baseCategory.comp
                    middleAssociator.hom
                    rightMiddleTwo.snd)
                  (baseCategory.comp
                    leftSecondTriple.fst
                    secondThird.fst)) := by
            rw [
              baseCategory.comp_assoc
                middleAssociator.hom
                rightMiddleTwo.snd
                (baseCategory.comp
                  leftSecondTriple.fst
                  secondThird.fst)
            ]
          _ = baseCategory.comp
                firstWhisker.arrow
                (baseCategory.comp
                  (baseCategory.comp
                    (baseCategory.comp
                      middleAssociator.hom
                      rightMiddleTwo.snd)
                    leftSecondTriple.fst)
                  secondThird.fst) := by
            rw [
              baseCategory.comp_assoc
                (baseCategory.comp
                  middleAssociator.hom
                  rightMiddleTwo.snd)
                leftSecondTriple.fst
                secondThird.fst
            ]
      _ = baseCategory.comp
            firstWhisker.arrow
            (baseCategory.comp
              (baseCategory.comp rightMiddleOne.fst rightFirstTriple.snd)
              secondThird.fst) := by
        rw [middleSecond]
      _ = baseCategory.comp
            (baseCategory.comp firstWhisker.arrow rightMiddleOne.fst)
            (baseCategory.comp rightFirstTriple.snd secondThird.fst) := by
        calc
          baseCategory.comp
              firstWhisker.arrow
              (baseCategory.comp
                (baseCategory.comp rightMiddleOne.fst rightFirstTriple.snd)
                secondThird.fst) =
              baseCategory.comp
                firstWhisker.arrow
                (baseCategory.comp
                  rightMiddleOne.fst
                  (baseCategory.comp rightFirstTriple.snd secondThird.fst)) := by
            rw [
              baseCategory.comp_assoc
                rightMiddleOne.fst
                rightFirstTriple.snd
                secondThird.fst
            ]
          _ = baseCategory.comp
                (baseCategory.comp firstWhisker.arrow rightMiddleOne.fst)
                (baseCategory.comp rightFirstTriple.snd secondThird.fst) := by
            exact
              (baseCategory.comp_assoc
                firstWhisker.arrow
                rightMiddleOne.fst
                (baseCategory.comp
                  rightFirstTriple.snd
                  secondThird.fst)).symm
      _ = baseCategory.comp
            (baseCategory.comp sourceOuter.fst firstAssociator.hom)
            (baseCategory.comp rightFirstTriple.snd secondThird.fst) := by
        rw [firstWhiskerFirst]
      _ = baseCategory.comp
            sourceOuter.fst
            (baseCategory.comp
              (baseCategory.comp firstAssociator.hom rightFirstTriple.snd)
              secondThird.fst) := by
        calc
          baseCategory.comp
              (baseCategory.comp sourceOuter.fst firstAssociator.hom)
              (baseCategory.comp rightFirstTriple.snd secondThird.fst) =
              baseCategory.comp
                sourceOuter.fst
                (baseCategory.comp
                  firstAssociator.hom
                  (baseCategory.comp
                    rightFirstTriple.snd
                    secondThird.fst)) :=
            baseCategory.comp_assoc
              sourceOuter.fst
              firstAssociator.hom
              (baseCategory.comp
                rightFirstTriple.snd
                secondThird.fst)
          _ = baseCategory.comp
                sourceOuter.fst
                (baseCategory.comp
                  (baseCategory.comp
                    firstAssociator.hom
                    rightFirstTriple.snd)
                  secondThird.fst) := by
            rw [
              baseCategory.comp_assoc
                firstAssociator.hom
                rightFirstTriple.snd
                secondThird.fst
            ]
      _ = baseCategory.comp
            sourceOuter.fst
            (baseCategory.comp sourceTriple.fst firstSecond.snd) := by
        rw [firstAssociatorSecond]

/-- Both canonical pentagon paths have the same flattened projection to the
third constituent span. -/
theorem canonicalPentagon_third_projection
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D E : baseCategory.Facet}
    (first : StructuralSpan baseCategory A B)
    (second : StructuralSpan baseCategory B C)
    (third : StructuralSpan baseCategory C D)
    (fourth : StructuralSpan baseCategory D E) :
    let thirdFourth :=
      selected.select third.targetLeg fourth.sourceLeg
    let secondRest :=
      selected.select
        second.targetLeg
        (baseCategory.comp thirdFourth.fst third.sourceLeg)
    let targetOuter :=
      selected.select
        first.targetLeg
        (baseCategory.comp secondRest.fst second.sourceLeg)
    baseCategory.comp
        (baseCategory.comp
          (baseCategory.comp
            (canonicalPentagonLeftPath
              selected first second third fourth).arrow
            targetOuter.snd)
          secondRest.snd)
        thirdFourth.fst =
      baseCategory.comp
        (baseCategory.comp
          (baseCategory.comp
            (canonicalPentagonRightPath
              selected first second third fourth).arrow
            targetOuter.snd)
          secondRest.snd)
        thirdFourth.fst := by
  dsimp only
  let firstSecond :=
    selected.select first.targetLeg second.sourceLeg
  let secondThird :=
    selected.select second.targetLeg third.sourceLeg
  let thirdFourth :=
    selected.select third.targetLeg fourth.sourceLeg
  let sourceTriple :=
    selected.select
      (baseCategory.comp firstSecond.snd second.targetLeg)
      third.sourceLeg
  let sourceOuter :=
    selected.select
      (baseCategory.comp sourceTriple.snd third.targetLeg)
      fourth.sourceLeg
  let leftMiddle :=
    selected.select
      (baseCategory.comp firstSecond.snd second.targetLeg)
      (baseCategory.comp thirdFourth.fst third.sourceLeg)
  let rightFirstTriple :=
    selected.select
      first.targetLeg
      (baseCategory.comp secondThird.fst second.sourceLeg)
  let rightMiddleOne :=
    selected.select
      (baseCategory.comp
        rightFirstTriple.snd
        (baseCategory.comp secondThird.snd third.targetLeg))
      fourth.sourceLeg
  let leftSecondTriple :=
    selected.select
      (baseCategory.comp secondThird.snd third.targetLeg)
      fourth.sourceLeg
  let rightMiddleTwo :=
    selected.select
      first.targetLeg
      (baseCategory.comp
        leftSecondTriple.fst
        (baseCategory.comp secondThird.fst second.sourceLeg))
  let rightSecondTriple :=
    selected.select
      second.targetLeg
      (baseCategory.comp thirdFourth.fst third.sourceLeg)
  let targetOuter :=
    selected.select
      first.targetLeg
      (baseCategory.comp rightSecondTriple.fst second.sourceLeg)
  let leftOuterAssociator :=
    canonicalAssociator
      selected
      (StructuralSpan.compose selected first second)
      third
      fourth
  let leftInnerAssociator :=
    canonicalAssociator
      selected
      first
      second
      (StructuralSpan.compose selected third fourth)
  let firstAssociator :=
    canonicalAssociator selected first second third
  let firstWhisker :=
    SpanTwoCell.horizontal
      selected
      firstAssociator.homCell
      (SpanTwoCell.identity fourth)
  let middleAssociator :=
    canonicalAssociator
      selected
      first
      (StructuralSpan.compose selected second third)
      fourth
  let lastAssociator :=
    canonicalAssociator selected second third fourth
  let lastWhisker :=
    SpanTwoCell.horizontal
      selected
      (SpanTwoCell.identity first)
      lastAssociator.homCell
  have leftInnerThird :
      baseCategory.comp
          (baseCategory.comp
            leftInnerAssociator.hom
            targetOuter.snd)
          rightSecondTriple.snd =
        leftMiddle.snd :=
    canonicalAssociatorHom_third
      selected
      first
      second
      (StructuralSpan.compose selected third fourth)
  have leftOuterSecond :
      baseCategory.comp
          (baseCategory.comp leftOuterAssociator.hom leftMiddle.snd)
          thirdFourth.fst =
        baseCategory.comp sourceOuter.fst sourceTriple.snd :=
    canonicalAssociatorHom_second
      selected
      (StructuralSpan.compose selected first second)
      third
      fourth
  have firstAssociatorThird :
      baseCategory.comp
          (baseCategory.comp firstAssociator.hom rightFirstTriple.snd)
          secondThird.snd =
        sourceTriple.snd :=
    canonicalAssociatorHom_third
      selected
      first
      second
      third
  have firstWhiskerFirst :
      baseCategory.comp firstWhisker.arrow rightMiddleOne.fst =
        baseCategory.comp sourceOuter.fst firstAssociator.hom :=
    SpanTwoCell.horizontal_first_projection
      selected
      firstAssociator.homCell
      (SpanTwoCell.identity fourth)
  have middleSecond :
      baseCategory.comp
          (baseCategory.comp middleAssociator.hom rightMiddleTwo.snd)
          leftSecondTriple.fst =
        baseCategory.comp rightMiddleOne.fst rightFirstTriple.snd :=
    canonicalAssociatorHom_second
      selected
      first
      (StructuralSpan.compose selected second third)
      fourth
  have lastAssociatorSecond :
      baseCategory.comp
          (baseCategory.comp lastAssociator.hom rightSecondTriple.snd)
          thirdFourth.fst =
        baseCategory.comp leftSecondTriple.fst secondThird.snd :=
    canonicalAssociatorHom_second
      selected
      second
      third
      fourth
  have lastWhiskerSecond :
      baseCategory.comp lastWhisker.arrow targetOuter.snd =
        baseCategory.comp rightMiddleTwo.snd lastAssociator.hom :=
    SpanTwoCell.horizontal_second_projection
      selected
      (SpanTwoCell.identity first)
      lastAssociator.homCell
  have rightPathArrow :
      (canonicalPentagonRightPath
        selected first second third fourth).arrow =
        baseCategory.comp
          firstWhisker.arrow
          (baseCategory.comp middleAssociator.hom lastWhisker.arrow) := by
    dsimp [
      canonicalPentagonRightPath,
      SpanTwoCell.vertical,
      SpanIsomorphism.homCell,
      firstWhisker,
      middleAssociator,
      lastWhisker
    ]
  have leftPathArrow :
      (canonicalPentagonLeftPath
        selected first second third fourth).arrow =
        baseCategory.comp
          leftOuterAssociator.hom
          leftInnerAssociator.hom := by
    dsimp [
      canonicalPentagonLeftPath,
      SpanTwoCell.vertical,
      SpanIsomorphism.homCell,
      leftOuterAssociator,
      leftInnerAssociator
    ]
  trans baseCategory.comp sourceOuter.fst sourceTriple.snd
  · calc
      baseCategory.comp
          (baseCategory.comp
            (baseCategory.comp
              (canonicalPentagonLeftPath
                selected first second third fourth).arrow
              targetOuter.snd)
            rightSecondTriple.snd)
          thirdFourth.fst =
          baseCategory.comp
            leftOuterAssociator.hom
            (baseCategory.comp
              (baseCategory.comp
                (baseCategory.comp
                  leftInnerAssociator.hom
                  targetOuter.snd)
                rightSecondTriple.snd)
              thirdFourth.fst) := by
        calc
          baseCategory.comp
              (baseCategory.comp
                (baseCategory.comp
                  (canonicalPentagonLeftPath
                    selected first second third fourth).arrow
                  targetOuter.snd)
                rightSecondTriple.snd)
              thirdFourth.fst =
              baseCategory.comp
                (canonicalPentagonLeftPath
                  selected first second third fourth).arrow
                (baseCategory.comp
                  targetOuter.snd
                  (baseCategory.comp
                    rightSecondTriple.snd
                    thirdFourth.fst)) := by
            calc
              _ = baseCategory.comp
                    (canonicalPentagonLeftPath
                      selected first second third fourth).arrow
                    (baseCategory.comp
                      (baseCategory.comp
                        targetOuter.snd
                        rightSecondTriple.snd)
                      thirdFourth.fst) :=
                baseCategory.comp_four_middle
                  (canonicalPentagonLeftPath
                    selected first second third fourth).arrow
                  targetOuter.snd
                  rightSecondTriple.snd
                  thirdFourth.fst
              _ = _ := by
                rw [
                  baseCategory.comp_assoc
                    targetOuter.snd
                    rightSecondTriple.snd
                    thirdFourth.fst
                ]
          _ = baseCategory.comp
                leftOuterAssociator.hom
                (baseCategory.comp
                  leftInnerAssociator.hom
                  (baseCategory.comp
                    targetOuter.snd
                    (baseCategory.comp
                      rightSecondTriple.snd
                      thirdFourth.fst))) := by
            rw [leftPathArrow]
            exact
              baseCategory.comp_assoc
                leftOuterAssociator.hom
                leftInnerAssociator.hom
                (baseCategory.comp
                  targetOuter.snd
                  (baseCategory.comp
                    rightSecondTriple.snd
                    thirdFourth.fst))
          _ = baseCategory.comp
                leftOuterAssociator.hom
                (baseCategory.comp
                  (baseCategory.comp
                    leftInnerAssociator.hom
                    targetOuter.snd)
                  (baseCategory.comp
                    rightSecondTriple.snd
                    thirdFourth.fst)) := by
            rw [
              baseCategory.comp_assoc
                leftInnerAssociator.hom
                targetOuter.snd
                (baseCategory.comp
                  rightSecondTriple.snd
                  thirdFourth.fst)
            ]
          _ = baseCategory.comp
                leftOuterAssociator.hom
                (baseCategory.comp
                  (baseCategory.comp
                    (baseCategory.comp
                      leftInnerAssociator.hom
                      targetOuter.snd)
                    rightSecondTriple.snd)
                  thirdFourth.fst) := by
            rw [
              baseCategory.comp_assoc
                (baseCategory.comp
                  leftInnerAssociator.hom
                  targetOuter.snd)
                rightSecondTriple.snd
                thirdFourth.fst
            ]
      _ = baseCategory.comp
            leftOuterAssociator.hom
            (baseCategory.comp leftMiddle.snd thirdFourth.fst) := by
        rw [leftInnerThird]
      _ = baseCategory.comp
            (baseCategory.comp leftOuterAssociator.hom leftMiddle.snd)
            thirdFourth.fst := by
        exact
          (baseCategory.comp_assoc
            leftOuterAssociator.hom
            leftMiddle.snd
            thirdFourth.fst).symm
      _ = baseCategory.comp sourceOuter.fst sourceTriple.snd :=
        leftOuterSecond
  · symm
    calc
      baseCategory.comp
          (baseCategory.comp
            (baseCategory.comp
              (canonicalPentagonRightPath
                selected first second third fourth).arrow
              targetOuter.snd)
            rightSecondTriple.snd)
          thirdFourth.fst =
          baseCategory.comp
            firstWhisker.arrow
            (baseCategory.comp
              middleAssociator.hom
              (baseCategory.comp
                (baseCategory.comp
                  (baseCategory.comp lastWhisker.arrow targetOuter.snd)
                  rightSecondTriple.snd)
                thirdFourth.fst)) := by
        rw [rightPathArrow]
        calc
          baseCategory.comp
              (baseCategory.comp
                (baseCategory.comp
                  (baseCategory.comp
                    firstWhisker.arrow
                    (baseCategory.comp
                      middleAssociator.hom
                      lastWhisker.arrow))
                  targetOuter.snd)
                rightSecondTriple.snd)
              thirdFourth.fst =
              baseCategory.comp
                firstWhisker.arrow
                (baseCategory.comp
                  (baseCategory.comp
                    middleAssociator.hom
                    lastWhisker.arrow)
                  (baseCategory.comp
                    targetOuter.snd
                    (baseCategory.comp
                      rightSecondTriple.snd
                      thirdFourth.fst))) :=
            baseCategory.comp_five_right
              firstWhisker.arrow
              (baseCategory.comp
                middleAssociator.hom
                lastWhisker.arrow)
              targetOuter.snd
              rightSecondTriple.snd
              thirdFourth.fst
          _ = baseCategory.comp
                firstWhisker.arrow
                (baseCategory.comp
                  middleAssociator.hom
                  (baseCategory.comp
                    lastWhisker.arrow
                    (baseCategory.comp
                      targetOuter.snd
                      (baseCategory.comp
                        rightSecondTriple.snd
                        thirdFourth.fst)))) :=
            congrArg
              (fun arrow =>
                baseCategory.comp firstWhisker.arrow arrow)
              (baseCategory.comp_assoc
                middleAssociator.hom
                lastWhisker.arrow
                (baseCategory.comp
                  targetOuter.snd
                  (baseCategory.comp
                    rightSecondTriple.snd
                    thirdFourth.fst)))
          _ = baseCategory.comp
                firstWhisker.arrow
                (baseCategory.comp
                  middleAssociator.hom
                  (baseCategory.comp
                    (baseCategory.comp
                      (baseCategory.comp
                        lastWhisker.arrow
                        targetOuter.snd)
                      rightSecondTriple.snd)
                    thirdFourth.fst)) := by
            rw [
              baseCategory.comp_assoc
                (baseCategory.comp
                  lastWhisker.arrow
                  targetOuter.snd)
                rightSecondTriple.snd
                thirdFourth.fst,
              baseCategory.comp_assoc
                lastWhisker.arrow
                targetOuter.snd
                (baseCategory.comp
                  rightSecondTriple.snd
                  thirdFourth.fst)
            ]
      _ = baseCategory.comp
            firstWhisker.arrow
            (baseCategory.comp
              middleAssociator.hom
              (baseCategory.comp
                (baseCategory.comp
                  (baseCategory.comp
                    rightMiddleTwo.snd
                    lastAssociator.hom)
                  rightSecondTriple.snd)
                thirdFourth.fst)) := by
        rw [lastWhiskerSecond]
      _ = baseCategory.comp
            firstWhisker.arrow
            (baseCategory.comp
              middleAssociator.hom
              (baseCategory.comp
                rightMiddleTwo.snd
                (baseCategory.comp
                  (baseCategory.comp
                    lastAssociator.hom
                    rightSecondTriple.snd)
                  thirdFourth.fst))) := by
        calc
          _ = baseCategory.comp
                firstWhisker.arrow
                (baseCategory.comp
                  middleAssociator.hom
                  (baseCategory.comp
                    rightMiddleTwo.snd
                    (baseCategory.comp
                      lastAssociator.hom
                      (baseCategory.comp
                        rightSecondTriple.snd
                        thirdFourth.fst)))) := by
            rw [
              baseCategory.comp_assoc
                (baseCategory.comp
                  rightMiddleTwo.snd
                  lastAssociator.hom)
                rightSecondTriple.snd
                thirdFourth.fst,
              baseCategory.comp_assoc
                rightMiddleTwo.snd
                lastAssociator.hom
                (baseCategory.comp
                  rightSecondTriple.snd
                  thirdFourth.fst)
            ]
          _ = _ :=
            congrArg
              (fun arrow =>
                baseCategory.comp
                  firstWhisker.arrow
                  (baseCategory.comp
                    middleAssociator.hom
                    (baseCategory.comp rightMiddleTwo.snd arrow)))
              (baseCategory.comp_assoc
                lastAssociator.hom
                rightSecondTriple.snd
                thirdFourth.fst).symm
      _ = baseCategory.comp
            firstWhisker.arrow
            (baseCategory.comp
              middleAssociator.hom
              (baseCategory.comp
                rightMiddleTwo.snd
                (baseCategory.comp
                  leftSecondTriple.fst
                  secondThird.snd))) := by
        rw [lastAssociatorSecond]
      _ = baseCategory.comp
            firstWhisker.arrow
            (baseCategory.comp
              (baseCategory.comp
                (baseCategory.comp
                  middleAssociator.hom
                  rightMiddleTwo.snd)
                leftSecondTriple.fst)
              secondThird.snd) := by
        rw [
          baseCategory.comp_assoc
            (baseCategory.comp
              middleAssociator.hom
              rightMiddleTwo.snd)
            leftSecondTriple.fst
            secondThird.snd,
          baseCategory.comp_assoc
            middleAssociator.hom
            rightMiddleTwo.snd
            (baseCategory.comp leftSecondTriple.fst secondThird.snd)
        ]
      _ = baseCategory.comp
            firstWhisker.arrow
            (baseCategory.comp
              (baseCategory.comp rightMiddleOne.fst rightFirstTriple.snd)
              secondThird.snd) := by
        rw [middleSecond]
      _ = baseCategory.comp
            (baseCategory.comp firstWhisker.arrow rightMiddleOne.fst)
            (baseCategory.comp rightFirstTriple.snd secondThird.snd) := by
        rw [
          baseCategory.comp_assoc
            rightMiddleOne.fst
            rightFirstTriple.snd
            secondThird.snd,
          baseCategory.comp_assoc
            firstWhisker.arrow
            rightMiddleOne.fst
            (baseCategory.comp rightFirstTriple.snd secondThird.snd)
        ]
      _ = baseCategory.comp
            (baseCategory.comp sourceOuter.fst firstAssociator.hom)
            (baseCategory.comp rightFirstTriple.snd secondThird.snd) := by
        rw [firstWhiskerFirst]
      _ = baseCategory.comp
            sourceOuter.fst
            (baseCategory.comp
              (baseCategory.comp firstAssociator.hom rightFirstTriple.snd)
              secondThird.snd) := by
        rw [
          baseCategory.comp_assoc
            firstAssociator.hom
            rightFirstTriple.snd
            secondThird.snd,
          baseCategory.comp_assoc
            sourceOuter.fst
            firstAssociator.hom
            (baseCategory.comp rightFirstTriple.snd secondThird.snd)
        ]
      _ = baseCategory.comp sourceOuter.fst sourceTriple.snd := by
        rw [firstAssociatorThird]

/-- Both canonical pentagon paths have the same flattened projection to the
fourth constituent span. -/
theorem canonicalPentagon_fourth_projection
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory)
    {A B C D E : baseCategory.Facet}
    (first : StructuralSpan baseCategory A B)
    (second : StructuralSpan baseCategory B C)
    (third : StructuralSpan baseCategory C D)
    (fourth : StructuralSpan baseCategory D E) :
    let thirdFourth :=
      selected.select third.targetLeg fourth.sourceLeg
    let secondRest :=
      selected.select
        second.targetLeg
        (baseCategory.comp thirdFourth.fst third.sourceLeg)
    let targetOuter :=
      selected.select
        first.targetLeg
        (baseCategory.comp secondRest.fst second.sourceLeg)
    baseCategory.comp
        (baseCategory.comp
          (baseCategory.comp
            (canonicalPentagonLeftPath
              selected first second third fourth).arrow
            targetOuter.snd)
          secondRest.snd)
        thirdFourth.snd =
      baseCategory.comp
        (baseCategory.comp
          (baseCategory.comp
            (canonicalPentagonRightPath
              selected first second third fourth).arrow
            targetOuter.snd)
          secondRest.snd)
        thirdFourth.snd := by
  dsimp only
  let firstSecond :=
    selected.select first.targetLeg second.sourceLeg
  let secondThird :=
    selected.select second.targetLeg third.sourceLeg
  let thirdFourth :=
    selected.select third.targetLeg fourth.sourceLeg
  let sourceTriple :=
    selected.select
      (baseCategory.comp firstSecond.snd second.targetLeg)
      third.sourceLeg
  let sourceOuter :=
    selected.select
      (baseCategory.comp sourceTriple.snd third.targetLeg)
      fourth.sourceLeg
  let leftMiddle :=
    selected.select
      (baseCategory.comp firstSecond.snd second.targetLeg)
      (baseCategory.comp thirdFourth.fst third.sourceLeg)
  let secondThirdComposite :=
    StructuralSpan.compose selected second third
  let rightFirstTriple :=
    selected.select
      first.targetLeg
      (baseCategory.comp secondThird.fst second.sourceLeg)
  let rightMiddleOne :=
    selected.select
      (baseCategory.comp
        rightFirstTriple.snd
        (baseCategory.comp secondThird.snd third.targetLeg))
      fourth.sourceLeg
  let leftSecondTriple :=
    selected.select
      (baseCategory.comp secondThird.snd third.targetLeg)
      fourth.sourceLeg
  let rightMiddleTwo :=
    selected.select
      first.targetLeg
      (baseCategory.comp
        leftSecondTriple.fst
        (baseCategory.comp secondThird.fst second.sourceLeg))
  let rightSecondTriple :=
    selected.select
      second.targetLeg
      (baseCategory.comp thirdFourth.fst third.sourceLeg)
  let targetOuter :=
    selected.select
      first.targetLeg
      (baseCategory.comp rightSecondTriple.fst second.sourceLeg)
  let leftOuterAssociator :=
    canonicalAssociator
      selected
      (StructuralSpan.compose selected first second)
      third
      fourth
  let leftInnerAssociator :=
    canonicalAssociator
      selected
      first
      second
      (StructuralSpan.compose selected third fourth)
  let firstAssociator :=
    canonicalAssociator selected first second third
  let firstWhisker :=
    SpanTwoCell.horizontal
      selected
      firstAssociator.homCell
      (SpanTwoCell.identity fourth)
  let middleAssociator :=
    canonicalAssociator
      selected
      first
      secondThirdComposite
      fourth
  let lastAssociator :=
    canonicalAssociator selected second third fourth
  let lastWhisker :=
    SpanTwoCell.horizontal
      selected
      (SpanTwoCell.identity first)
      lastAssociator.homCell
  have leftInnerThird :
      baseCategory.comp
          (baseCategory.comp
            leftInnerAssociator.hom
            targetOuter.snd)
          rightSecondTriple.snd =
        leftMiddle.snd :=
    canonicalAssociatorHom_third
      selected
      first
      second
      (StructuralSpan.compose selected third fourth)
  have leftOuterThird :
      baseCategory.comp
          (baseCategory.comp leftOuterAssociator.hom leftMiddle.snd)
          thirdFourth.snd =
        sourceOuter.snd :=
    canonicalAssociatorHom_third
      selected
      (StructuralSpan.compose selected first second)
      third
      fourth
  have firstWhiskerSecond :
      baseCategory.comp firstWhisker.arrow rightMiddleOne.snd =
        baseCategory.comp
          sourceOuter.snd
          (baseCategory.id fourth.apex) :=
    SpanTwoCell.horizontal_second_projection
      selected
      firstAssociator.homCell
      (SpanTwoCell.identity fourth)
  have middleThird :
      baseCategory.comp
          (baseCategory.comp middleAssociator.hom rightMiddleTwo.snd)
          leftSecondTriple.snd =
        rightMiddleOne.snd :=
    canonicalAssociatorHom_third
      selected
      first
      secondThirdComposite
      fourth
  have lastAssociatorThird :
      baseCategory.comp
          (baseCategory.comp lastAssociator.hom rightSecondTriple.snd)
          thirdFourth.snd =
        leftSecondTriple.snd :=
    canonicalAssociatorHom_third
      selected
      second
      third
      fourth
  have lastWhiskerSecond :
      baseCategory.comp lastWhisker.arrow targetOuter.snd =
        baseCategory.comp rightMiddleTwo.snd lastAssociator.hom :=
    SpanTwoCell.horizontal_second_projection
      selected
      (SpanTwoCell.identity first)
      lastAssociator.homCell
  have rightPathArrow :
      (canonicalPentagonRightPath
        selected first second third fourth).arrow =
        baseCategory.comp
          firstWhisker.arrow
          (baseCategory.comp middleAssociator.hom lastWhisker.arrow) := by
    dsimp [
      canonicalPentagonRightPath,
      SpanTwoCell.vertical,
      SpanIsomorphism.homCell,
      firstWhisker,
      middleAssociator,
      secondThirdComposite,
      lastWhisker
    ]
  have leftPathArrow :
      (canonicalPentagonLeftPath
        selected first second third fourth).arrow =
        baseCategory.comp
          leftOuterAssociator.hom
          leftInnerAssociator.hom := by
    dsimp [
      canonicalPentagonLeftPath,
      SpanTwoCell.vertical,
      SpanIsomorphism.homCell,
      leftOuterAssociator,
      leftInnerAssociator
    ]
  trans sourceOuter.snd
  · calc
      baseCategory.comp
          (baseCategory.comp
            (baseCategory.comp
              (canonicalPentagonLeftPath
                selected first second third fourth).arrow
              targetOuter.snd)
            rightSecondTriple.snd)
          thirdFourth.snd =
          baseCategory.comp
            leftOuterAssociator.hom
            (baseCategory.comp
              (baseCategory.comp
                (baseCategory.comp
                  leftInnerAssociator.hom
                  targetOuter.snd)
                rightSecondTriple.snd)
              thirdFourth.snd) := by
        rw [leftPathArrow]
        calc
          baseCategory.comp
              (baseCategory.comp
                (baseCategory.comp
                  (baseCategory.comp
                    leftOuterAssociator.hom
                    leftInnerAssociator.hom)
                  targetOuter.snd)
                rightSecondTriple.snd)
              thirdFourth.snd =
              baseCategory.comp
                leftOuterAssociator.hom
                (baseCategory.comp
                  leftInnerAssociator.hom
                  (baseCategory.comp
                    targetOuter.snd
                    (baseCategory.comp
                      rightSecondTriple.snd
                      thirdFourth.snd))) :=
            baseCategory.comp_five_right
              leftOuterAssociator.hom
              leftInnerAssociator.hom
              targetOuter.snd
              rightSecondTriple.snd
              thirdFourth.snd
          _ = baseCategory.comp
                leftOuterAssociator.hom
                (baseCategory.comp
                  (baseCategory.comp
                    leftInnerAssociator.hom
                    targetOuter.snd)
                  (baseCategory.comp
                    rightSecondTriple.snd
                    thirdFourth.snd)) := by
            rw [
              baseCategory.comp_assoc
                leftInnerAssociator.hom
                targetOuter.snd
                (baseCategory.comp
                  rightSecondTriple.snd
                  thirdFourth.snd)
            ]
          _ = baseCategory.comp
                leftOuterAssociator.hom
                (baseCategory.comp
                  (baseCategory.comp
                    (baseCategory.comp
                      leftInnerAssociator.hom
                      targetOuter.snd)
                    rightSecondTriple.snd)
                  thirdFourth.snd) := by
            rw [
              baseCategory.comp_assoc
                (baseCategory.comp
                  leftInnerAssociator.hom
                  targetOuter.snd)
                rightSecondTriple.snd
                thirdFourth.snd
            ]
      _ = baseCategory.comp
            leftOuterAssociator.hom
            (baseCategory.comp leftMiddle.snd thirdFourth.snd) := by
        rw [leftInnerThird]
      _ = baseCategory.comp
            (baseCategory.comp leftOuterAssociator.hom leftMiddle.snd)
            thirdFourth.snd := by
        exact
          (baseCategory.comp_assoc
            leftOuterAssociator.hom
            leftMiddle.snd
            thirdFourth.snd).symm
      _ = sourceOuter.snd :=
        leftOuterThird
  · symm
    calc
      baseCategory.comp
          (baseCategory.comp
            (baseCategory.comp
              (canonicalPentagonRightPath
                selected first second third fourth).arrow
              targetOuter.snd)
            rightSecondTriple.snd)
          thirdFourth.snd =
          baseCategory.comp
            firstWhisker.arrow
            (baseCategory.comp
              middleAssociator.hom
              (baseCategory.comp
                (baseCategory.comp
                  (baseCategory.comp lastWhisker.arrow targetOuter.snd)
                  rightSecondTriple.snd)
                thirdFourth.snd)) := by
        rw [rightPathArrow]
        calc
          baseCategory.comp
              (baseCategory.comp
                (baseCategory.comp
                  (baseCategory.comp
                    firstWhisker.arrow
                    (baseCategory.comp
                      middleAssociator.hom
                      lastWhisker.arrow))
                  targetOuter.snd)
                rightSecondTriple.snd)
              thirdFourth.snd =
              baseCategory.comp
                firstWhisker.arrow
                (baseCategory.comp
                  (baseCategory.comp
                    middleAssociator.hom
                    lastWhisker.arrow)
                  (baseCategory.comp
                    targetOuter.snd
                    (baseCategory.comp
                      rightSecondTriple.snd
                      thirdFourth.snd))) :=
            baseCategory.comp_five_right
              firstWhisker.arrow
              (baseCategory.comp
                middleAssociator.hom
                lastWhisker.arrow)
              targetOuter.snd
              rightSecondTriple.snd
              thirdFourth.snd
          _ = baseCategory.comp
                firstWhisker.arrow
                (baseCategory.comp
                  middleAssociator.hom
                  (baseCategory.comp
                    lastWhisker.arrow
                    (baseCategory.comp
                      targetOuter.snd
                      (baseCategory.comp
                        rightSecondTriple.snd
                        thirdFourth.snd)))) :=
            congrArg
              (fun arrow =>
                baseCategory.comp firstWhisker.arrow arrow)
              (baseCategory.comp_assoc
                middleAssociator.hom
                lastWhisker.arrow
                (baseCategory.comp
                  targetOuter.snd
                  (baseCategory.comp
                    rightSecondTriple.snd
                    thirdFourth.snd)))
          _ = baseCategory.comp
                firstWhisker.arrow
                (baseCategory.comp
                  middleAssociator.hom
                  (baseCategory.comp
                    (baseCategory.comp
                      (baseCategory.comp
                        lastWhisker.arrow
                        targetOuter.snd)
                      rightSecondTriple.snd)
                    thirdFourth.snd)) := by
            rw [
              baseCategory.comp_assoc
                (baseCategory.comp
                  lastWhisker.arrow
                  targetOuter.snd)
                rightSecondTriple.snd
                thirdFourth.snd,
              baseCategory.comp_assoc
                lastWhisker.arrow
                targetOuter.snd
                (baseCategory.comp
                  rightSecondTriple.snd
                  thirdFourth.snd)
            ]
      _ = baseCategory.comp
            firstWhisker.arrow
            (baseCategory.comp
              middleAssociator.hom
              (baseCategory.comp
                (baseCategory.comp
                  (baseCategory.comp
                    rightMiddleTwo.snd
                    lastAssociator.hom)
                  rightSecondTriple.snd)
                thirdFourth.snd)) := by
        rw [lastWhiskerSecond]
      _ = baseCategory.comp
            firstWhisker.arrow
            (baseCategory.comp
              middleAssociator.hom
              (baseCategory.comp
                rightMiddleTwo.snd
                (baseCategory.comp
                  (baseCategory.comp
                    lastAssociator.hom
                    rightSecondTriple.snd)
                  thirdFourth.snd))) := by
        calc
          _ = baseCategory.comp
                firstWhisker.arrow
                (baseCategory.comp
                  middleAssociator.hom
                  (baseCategory.comp
                    rightMiddleTwo.snd
                    (baseCategory.comp
                      lastAssociator.hom
                      (baseCategory.comp
                        rightSecondTriple.snd
                        thirdFourth.snd)))) := by
            rw [
              baseCategory.comp_assoc
                (baseCategory.comp
                  rightMiddleTwo.snd
                  lastAssociator.hom)
                rightSecondTriple.snd
                thirdFourth.snd,
              baseCategory.comp_assoc
                rightMiddleTwo.snd
                lastAssociator.hom
                (baseCategory.comp
                  rightSecondTriple.snd
                  thirdFourth.snd)
            ]
          _ = _ :=
            congrArg
              (fun arrow =>
                baseCategory.comp
                  firstWhisker.arrow
                  (baseCategory.comp
                    middleAssociator.hom
                    (baseCategory.comp rightMiddleTwo.snd arrow)))
              (baseCategory.comp_assoc
                lastAssociator.hom
                rightSecondTriple.snd
                thirdFourth.snd).symm
      _ = baseCategory.comp
            firstWhisker.arrow
            (baseCategory.comp
              middleAssociator.hom
              (baseCategory.comp
                rightMiddleTwo.snd
                leftSecondTriple.snd)) := by
        rw [lastAssociatorThird]
      _ = baseCategory.comp
            firstWhisker.arrow
            (baseCategory.comp
              (baseCategory.comp middleAssociator.hom rightMiddleTwo.snd)
              leftSecondTriple.snd) := by
        exact
          congrArg
            (fun arrow =>
              baseCategory.comp firstWhisker.arrow arrow)
            (baseCategory.comp_assoc
              middleAssociator.hom
              rightMiddleTwo.snd
              leftSecondTriple.snd).symm
      _ = baseCategory.comp firstWhisker.arrow rightMiddleOne.snd := by
        rw [middleThird]
      _ = baseCategory.comp
            sourceOuter.snd
            (baseCategory.id fourth.apex) := by
        rw [firstWhiskerSecond]
      _ = sourceOuter.snd :=
        baseCategory.comp_id sourceOuter.snd

/-- The canonical associators derived from selected pullbacks satisfy Mac
Lane's pentagon equation. The proof reduces equality of the two path arrows
to their four constituent projections and uses only pullback uniqueness plus
the base-category laws. -/
theorem canonicalSpanPentagon
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory) :
    SpanPentagonEquation
      (canonicalSpanComparisonData selected) := by
  intro A B C D E first second third fourth
  change
    canonicalPentagonLeftPath selected first second third fourth =
      canonicalPentagonRightPath selected first second third fourth
  apply SpanTwoCell.ext
  apply
    rightAssociatedFour_hom_ext
      selected
      first
      second
      third
      fourth
  · exact
      canonicalPentagon_first_projection
        selected
        first
        second
        third
        fourth
  · exact
      canonicalPentagon_second_projection
        selected
        first
        second
        third
        fourth
  · exact
      canonicalPentagon_third_projection
        selected
        first
        second
        third
        fourth
  · exact
      canonicalPentagon_fourth_projection
        selected
        first
        second
        third
        fourth

/-- Selected pullbacks constructively determine comparison data satisfying
both mechanized coherence equations. No `SpanCoherenceProof` is supplied as
trusted input. -/
def canonicalSpanCoherenceProof
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory) :
    SpanCoherenceProof (canonicalSpanComparisonData selected) where
  triangle := canonicalSpanTriangle selected
  pentagon := canonicalSpanPentagon selected

/-- Every supplied selected-pullback profile yields the exact coherence
package required by the Cycle 2 M10 condition. This does not assert that
selected pullbacks exist for an arbitrary facet category. -/
def canonicalSpanCoherencePackage
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig}
    (selected : SelectedPullbacks baseCategory) :
    SpanCoherencePackage baseCategory where
  selected := selected
  comparisons := canonicalSpanComparisonData selected
  coherence := canonicalSpanCoherenceProof selected

/-- The minimal constructive bridge into M10: existence of a selected
pullback profile implies the previously registered coherence condition. -/
theorem selectedPullbacks_imply_M10Condition
    {sig : StaticSignature}
    {baseCategory : FacetCategory sig} :
    Nonempty (SelectedPullbacks baseCategory) →
      M10SpanCompositionCoherenceCondition baseCategory := by
  rintro ⟨selected⟩
  exact ⟨canonicalSpanCoherencePackage selected⟩

end Caeluviim.RRKC.Cycle2
