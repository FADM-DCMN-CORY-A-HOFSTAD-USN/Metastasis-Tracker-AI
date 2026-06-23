#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "PhysicsEngine/PhysicsConstraintComponent.h"
#include "PycnogonidDegradationComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UPycnogonidDegradationComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPycnogonidDegradationComponent()
    {
        PrimaryComponentTick.bCanEverTick = true;
        StructuralIntegrity = 1.0f; // Start pristine
    }

    // Configurable parameters matching the JSON schema
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chemical Degradation")
    float OptimalPH = 8.1f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chemical Degradation")
    float AlkalineDegradationK = 0.018f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chemical Degradation")
    float AlkalineExponentB = 2.5f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chemical Degradation")
    float AcidDegradationK = 0.005f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chemical Degradation")
    float AcidExponentA = 2.2f;

    UPROPERTY(BlueprintReadOnly, Category = "Chemical Degradation")
    float StructuralIntegrity;

    // References to your 8 leg constraint components to modify torque limits dynamically
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Physics Assembly")
    TArray<UPhysicsConstraintComponent*> JointConstraints;

    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override
    {
        Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

        // 1. Fetch current runtime pH from the global simulator environment
        float CurrentPH = GetWorldEnvironmentPH(); 

        // 2. Compute Alkaline and Acidic delta offsets
        float AlkalineDelta = FMath::Max(0.0f, CurrentPH - OptimalPH);
        float AcidDelta = FMath::Max(0.0f, OptimalPH - CurrentPH);

        // 3. Calculate degradation rate via non-linear scaling equations
        float AlkalineDamage = AlkalineDegradationK * FMath::Pow(AlkalineDelta, AlkalineExponentB);
        float AcidDamage = AcidDegradationK * FMath::Pow(AcidDelta, AcidExponentA);
        
        float TotalDegradationRate = AlkalineDamage + AcidDamage;

        // 4. Update structural integrity variable over time step delta
        StructuralIntegrity -= TotalDegradationRate * DeltaTime;
        StructuralIntegrity = FMath::Clamp(StructuralIntegrity, 0.0f, 1.0f);

        // 5. Inject physical degradation directly into active joint constraint drives
        for (UPhysicsConstraintComponent* Constraint : JointConstraints)
        {
            if (Constraint)
            {
                // Retrieve original baseline parameters (configured at setup)
                float BaseStiffness = 5000.0f; 
                float BaseDamping = 250.0f;

                // Scale constraint physics directly down by chemical degradation scalar
                float NewStiffness = BaseStiffness * StructuralIntegrity;
                float NewDamping = BaseDamping * FMath::Max(0.1f, StructuralIntegrity);

                // Re-assign scaled values to active angular drive motors
                Constraint->SetAngularDriveParams(NewStiffness, NewDamping, 0.0f);
            }
        }

        // 6. Evaluate structural collapse bounds
        if (StructuralIntegrity <= 0.0f)
        {
            TriggerTotalStructuralLiquefaction();
        }
    }

private:
    float GetWorldEnvironmentPH()
    {
        // Mock method: replace with your global simulator's environmental variable query
        return 9.5f; 
    }

    void TriggerTotalStructuralLiquefaction()
    {
        // Total tissue failure: Disable physics constraints to turn the agent into a limp ragdoll
        for (UPhysicsConstraintComponent* Constraint : JointConstraints)
        {
            if (Constraint) Constraint->BreakConstraint();
        }
        GEngine->AddOnScreenDebugMessage(-1, 5.f, FColor::Red, TEXT("CRITICAL: Agent exoskeleton degraded entirely. Structural collapse achieved."));
    }
};
