#include "PycnogonidSubstepManager.h"
#include "PhysicsEngine/PhysicsConstraintComponent.h"
#include "Components/PrimitiveComponent.h"
// 1. Primary Class Header Link
#include "PycnogonidSubstepManager.h"

// 2. Objects Subsystem Header Links (Explicit paths matching the folder layout)
#include "objects/public/PycnogonidBiomassPayload.h"

// 3. Low-Level Unreal Engine Physics & Component System Modules
#include "PhysicsEngine/PhysicsConstraintComponent.h"
#include "Components/PrimitiveComponent.h"
#include "Math/UnrealMathUtility.h"

// ==============================================================================
// Implementation code continues below...
// ==============================================================================

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

#include "PycnogonidSubstepManager.h"
#include "objects/public/PycnogonidBiomassPayload.h"
#include "PhysicsEngine/PhysicsConstraintComponent.h"
#include "Components/PrimitiveComponent.h"

// Assuming an instance of the bridge is accessible to this component
// (e.g., as a member variable: FPycnogonidBiomassBridge BiomassBridge;)

void UPycnogonidSubstepManager::OnPhysicsSubstep(float SubstepDeltaTime, FBodyInstance* BodyInstance)
{
    if (!BodyInstance) return;

    // 1. Initialize a local storage container for the unboxed data
    FPycnogonidBiomassPayload UnboxedPayload;

    // 2. Perform a lock-free, atomic read from the main game loop thread
    // This completes in O(1) time without blocking the high-frequency physics thread
    if (BiomassBridge.ReadLatestState(UnboxedPayload))
    {
        // 3. Dynamically update the mass profile of the rigid body node
        // Forces physical gravity and momentum reactions to adjust to current nutritional values
        BodyInstance->SetBodyMass(UnboxedPayload.CurrentMassMg);

        // 4. Update the physical collision scale profile (Width/Thickness)
        // ConditionFactor > 1.0 expands the cylinder radius (Thick profile)
        // ConditionFactor < 1.0 compresses the cylinder radius (Skinny profile)
        FVector DynamicScale = FVector(UnboxedPayload.ConditionFactor, UnboxedPayload.ConditionFactor, 1.0f);
        BodyInstance->SetBodyScale(DynamicScale);
        
        // Update local tracking copy for subsequent un-triggered substeps
        SubstepStructuralIntegrity = UnboxedPayload.ConditionFactor;
    }

    // 5. Apply the resolved physical scales to the active joint motor drive systems
    float BaseStiffness = 5000.0f;
    float BaseDamping = 250.0f;

    // Joint stiffness drops linearly if structural integrity or thickness degrades
    float ScaledStiffness = BaseStiffness * SubstepStructuralIntegrity;
    float ScaledDamping = BaseDamping * FMath::Max(0.1f, SubstepStructuralIntegrity);

    for (UPhysicsConstraintComponent* Constraint : TargetConstraints)
    {
        if (Constraint)
        {
            // Inject scaled parameters straight into the low-level physics constraints matrix
            Constraint->SetAngularDriveParams(ScaledStiffness, ScaledDamping, 0.0f);
        }
    }
}
