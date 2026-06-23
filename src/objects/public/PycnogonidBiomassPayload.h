#pragma once

#include "CoreMinimal.h"
#include "PycnogonidBiomassPayload.generated.h"

// The pure data packet mirrored to the physics thread
USTRUCT(BlueprintType)
fstruct FPycnogonidBiomassPayload
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "Biomass Matrix")
    float ConditionFactor;       // Scales leg thickness profiles (Thick vs Skinny)

    UPROPERTY(BlueprintReadOnly, Category = "Biomass Matrix")
    float CurrentMassMg;         // Absolute wet mass for rigid body calculations

    UPROPERTY(BlueprintReadOnly, Category = "Biomass Matrix")
    float TotalCavityVolumeMm3;  // Total internal structural storage capacity

    UPROPERTY(BlueprintReadOnly, Category = "Biomass Matrix")
    int32 AvailableEggCount;     // Ready eggs computed via current protein mass bounds

    FPycnogonidBiomassPayload()
        : ConditionFactor(1.0f)
        , CurrentMassMg(1.0f)
        , TotalCavityVolumeMm3(1.45f)
        , AvailableEggCount(0)
    {}
};

// Lock-Free Double Buffer for Inter-Thread Communication
class FPycnogonidBiomassBridge
{
public:
    // Called by the main game loop thread when updating nutrient/protein arrays
    void WriteLatestState(const FPycnogonidBiomassPayload& InPayload)
    {
        BackBuffer = InPayload;
        bHasUpdate.store(true, std::memory_order_release);
    }

    // Called asynchronously by the Physics Substep thread to update rigid body constraints
    bool ReadLatestState(FPycnogonidBiomassPayload& OutPayload)
    {
        // Low-cost atomic evaluation avoids freezing the asynchronous physics thread
        if (bHasUpdate.load(std::memory_order_acquire))
        {
            OutPayload = BackBuffer;
            bHasUpdate.store(false, std::memory_order_relaxed);
            return true;
        }
        return false;
    }

private:
    FPycnogonidBiomassPayload BackBuffer;
    std::atomic<bool> bHasUpdate{false};
};
