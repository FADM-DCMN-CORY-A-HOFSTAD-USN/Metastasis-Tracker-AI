#include "PycnogonidSubstepManager.h"
#include "PhysicsEngine/PhysicsConstraintComponent.h"
#include "Components/PrimitiveComponent.h"

UPycnogonidSubstepManager::UPycnogonidSubstepManager()
{
    PrimaryComponentTick.bCanEverTick = true;
    SubstepStructuralIntegrity = 1.0f;
    RunPH = 9.5f; // Active scenario target value
}

void UPycnogonidSubstepManager::BeginPlay()
{
    Super::BeginPlay();

    // Check if we have an actor containing physics-driven primitive mesh components
    AActor* Owner = GetOwner();
    if (!Owner) return;

    UPrimitiveComponent* PrimeComp = Cast<UPrimitiveComponent>(Owner->GetComponentByClass(UPrimitiveComponent::StaticClass()));
    if (PrimeComp && PrimeComp->GetBodyInstance())
    {
        // 1. Construct the system callback delegate
        OnPhysicsSubstepDelegate.BindUObject(this, &UPycnogonidSubstepManager::OnPhysicsSubstep);
        
        // 2. Register the component instance directly into the sub-stepping thread loop
        PrimeComp->GetBodyInstance()->AddCustomPhysics(OnPhysicsSubstepDelegate);
    }
}

void UPycnogonidSubstepManager::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    // Re-register the custom sub-step worker for the next frame iteration
    AActor* Owner = GetOwner();
    if (Owner)
    {
        UPrimitiveComponent* PrimeComp = Cast<UPrimitiveComponent>(Owner->GetComponentByClass(UPrimitiveComponent::StaticClass()));
        if (PrimeComp && PrimeComp->GetBodyInstance())
        {
            PrimeComp->GetBodyInstance()->AddCustomPhysics(OnPhysicsSubstepDelegate);
        }
    }
}

// ==============================================================================
// ⏱️ ASYNCHRONOUS PHYSICS THREAD CALCULATION LOOP (Runs at independent fixed intervals)
// ==============================================================================
void UPycnogonidSubstepManager::OnPhysicsSubstep(float SubstepDeltaTime, FBodyInstance* BodyInstance)
{
    if (!BodyInstance) return;

    // Baseline calculation values mirrored locally for thread safety
    float OptimalPH = 8.1f;
    float AlkalineK = 0.018f;
    float AlkalineExp = 2.5f;

    // Resolve non-linear chemical delta calculations within the sub-step tick bounds
    float AlkalineDelta = FMath::Max(0.0f, RunPH - OptimalPH);
    float AlkalineDamage = AlkalineK * FMath::Pow(AlkalineDelta, AlkalineExp);

    // Apply incremental degradation matching the high-precision timeline split
    SubstepStructuralIntegrity -= AlkalineDamage * SubstepDeltaTime;
    SubstepStructuralIntegrity = FMath::Clamp(SubstepStructuralIntegrity, 0.0f, 1.0f);

    // Adjust joint physics limits smoothly during frame variance
    for (UPhysicsConstraintComponent* Constraint : TargetConstraints)
    {
        if (Constraint)
        {
            float BaseStiffness = 5000.0f;
            float NewStiffness = BaseStiffness * SubstepStructuralIntegrity;
            
            // Directly write to the constraint drive without relying on standard frame ticks
            Constraint->SetAngularDriveParams(NewStiffness, 250.0f, 0.0f);
        }
    }
}

void UPycnogonidSubstepManager::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // Cleanly unbind delegates on shutdown to protect headless command line tests from memory leaks
    OnPhysicsSubstepDelegate.Unbind();
    Super::EndPlay(EndPlayReason);
}
