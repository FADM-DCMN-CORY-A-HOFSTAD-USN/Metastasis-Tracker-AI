// Inside your custom asynchronous sub-step loop
FPycnogonidBiomassPayload LocalPayload;
if (BiomassBridge.ReadLatestState(LocalPayload))
{
    // Update rigid body mass definitions dynamically
    BodyInstance->SetBodyMass(LocalPayload.CurrentMassMg);
    
    // Scale structural geometry thickness calculations (X/Y local radii)
    FVector NewScale = FVector(LocalPayload.ConditionFactor, LocalPayload.ConditionFactor, 1.0f);
    BodyInstance->SetBodyScale(NewScale);
}
