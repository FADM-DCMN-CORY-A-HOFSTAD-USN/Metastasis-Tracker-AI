#include "PycnogonidDegradationComponent.h"

UPycnogonidDegradationComponent::UPycnogonidDegradationComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    
    // Assign structural baseline initializations
    StructuralIntegrity = 1.0f; 
    OptimalPH = 8.1f;
    AlkalineDegradationK = 0.018f;
    AlkalineExponentB = 2.5f;
    AcidDegradationK = 0.005f;
    AcidExponentA = 2.2f;
}

void UPycnogonidDegradationComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    // 1. Fetch live runtime pH context
    float CurrentPH = GetWorldEnvironmentPH(); 

    // 2. Compute pH deltas
    float AlkalineDelta = FMath::Max(0.0f, CurrentPH - OptimalPH);
    float AcidDelta = FMath::Max(0.0f, OptimalPH - CurrentPH);

    // 3. Compute non-linear damage values
    float AlkalineDamage = AlkalineDegradationK * FMath::Pow(AlkalineDelta, AlkalineExponentB);
    float AcidDamage = AcidDegradationK * FMath::Pow(AcidDelta, AcidExponentA);
    float TotalDegradationRate = AlkalineDamage + AcidDamage;

    // 4. Degrade integrity step
    StructuralIntegrity -= TotalDegradationRate * DeltaTime;
    StructuralIntegrity = FMath::Clamp(StructuralIntegrity, 0.0f, 1.0f);

    // 5. Update physical motor constraints
    for (UPhysicsConstraintComponent* Constraint : JointConstraints)
    {
        if (Constraint)
        {
            float BaseStiffness = 5000.0f; 
            float BaseDamping = 250.0f;

            float NewStiffness = BaseStiffness * StructuralIntegrity;
            float NewDamping = BaseDamping * FMath::Max(0.1f, StructuralIntegrity);

            Constraint->SetAngularDriveParams(NewStiffness, NewDamping, 0.0f);
        }
    }

    // 6. Check for total collapse bound
    if (StructuralIntegrity <= 0.0f)
    {
        TriggerTotalStructuralLiquefaction();
    }
}

float UPycnogonidDegradationComponent::GetWorldEnvironmentPH()
{
    // Replace with your global environment module connection
    return 9.5f; 
}

void UPycnogonidDegradationComponent::TriggerTotalStructuralLiquefaction()
{
    for (UPhysicsConstraintComponent* Constraint : JointConstraints)
    {
        if (Constraint) 
        {
            Constraint->BreakConstraint();
        }
    }
}
