#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "LarvalPoolManager.generated.h"

// Flyweight data representation maximizing CPU cache-locality
USTRUCT(BlueprintType)
struct FLarvaAgentNode
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "Larva Node")
    FVector Position;

    UPROPERTY(BlueprintReadOnly, Category = "Larva Node")
    FVector Velocity;

    UPROPERTY(BlueprintReadOnly, Category = "Larva Node")
    float DevelopmentIndex; // DI (0.0 to 1.0)

    UPROPERTY(BlueprintReadOnly, Category = "Larva Node")
    float YolkReserveMm3;

    UPROPERTY(BlueprintReadOnly, Category = "Larva Node")
    bool bIsActive;

    FLarvaAgentNode()
        : Position(FVector::ZeroVector)
        , Velocity(FVector::ZeroVector)
        , DevelopmentIndex(0.0f)
        , YolkReserveMm3(0.0f)
        , bIsActive(false)
    {}
};

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class METASTASISTRACKERAI_API ULarvalPoolManager : public UActorComponent
{
    GENERATED_BODY()

public:    
    ULarvalPoolManager();

    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

    // Headless batch initialization hook called during reproduction steps
    UFUNCTION(BlueprintCallable, Category = "Reproduction Loop")
    int32 ExecuteBatchSpawning(const FVector& OriginLocation, int32 SpawnCount, float ParentYolkAllocation);

    // Read-only metrics query for automation checks
    int32 GetActiveLarvaeCount() const { return ActiveLarvaeCount; }

private:
    // Flat stack allocation bounds preventing dynamic runtime heap allocations
    static const int32 POOL_SIZE_CEILING = 50000;
    
    // Contiguous memory array block
    TArray<FLarvaAgentNode> LarvaMemoryPool;
    
    int32 ActiveLarvaeCount;
    int32 FirstAvailableIndex;

    // Internal helper to scan for next open array index
    void UpdateFirstAvailableIndex();
};
