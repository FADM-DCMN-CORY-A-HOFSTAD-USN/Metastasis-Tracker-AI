#include "LarvalPoolManager.h"

ULarvalPoolManager::ULarvalPoolManager()
{
    PrimaryComponentTick.bCanEverTick = true;
    ActiveLarvaeCount = 0;
    FirstAvailableIndex = 0;
}

void ULarvalPoolManager::BeginPlay()
{
    Super::BeginPlay();

    // Reserve and construct the complete structural chunk at engine bootup
    LarvaMemoryPool.SetNumZeroed(POOL_SIZE_CEILING);
    UE_LOG(LogTemp, Log, TEXT("Pycnogonid Engine: Pre-allocated contiguous RAM block for %d larval slots."), POOL_SIZE_CEILING);
}

int32 ULarvalPoolManager::ExecuteBatchSpawning(const FVector& OriginLocation, int32 SpawnCount, float ParentYolkAllocation)
{
    int32 SuccessfullySpawned = 0;

    for (int32 i = 0; i < SpawnCount; ++i)
    {
        // Enforce boundary safety check against hard ceiling capacity limits
        if (FirstAvailableIndex >= POOL_SIZE_CEILING)
        {
            UE_LOG(LogTemp, Warning, TEXT("Reproduction Failure: Larva allocation pool has reached capacity saturation limits!"));
            break;
        }

        // Fetch reference to the pre-allocated block directly (O(1) matrix access)
        FLarvaAgentNode& TargetNode = LarvaMemoryPool[FirstAvailableIndex];

        // Wake the inactive node and initialize spatial data vectors
        TargetNode.bIsActive = true;
        TargetNode.Position = OriginLocation + FVector(FMath::RandRange(-5.f, 5.f), FMath::RandRange(-5.f, 5.f), 0.f);
        TargetNode.Velocity = FVector(0.f, 0.f, -1.2f); // Baseline sinking velocity
        TargetNode.DevelopmentIndex = 0.0f;
        TargetNode.YolkReserveMm3 = ParentYolkAllocation;

        SuccessfullySpawned++;
        ActiveLarvaeCount++;

        // Advance index trace marker forward to the next inactive node
        UpdateFirstAvailableIndex();
    }

    return SuccessfullySpawned;
}

void ULarvalPoolManager::UpdateFirstAvailableIndex()
{
    // Search forward from the current location to save processing loops
    for (int32 i = FirstAvailableIndex; i < POOL_SIZE_CEILING; ++i)
    {
        if (!LarvaMemoryPool[i].bIsActive)
        {
            FirstAvailableIndex = i;
            return;
        }
    }
    // If the loop completes with no match, the block array is saturated
    FirstAvailableIndex = POOL_SIZE_CEILING;
}

void ULarvalPoolManager::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    float LowReynoldsViscosity = 0.00108f;

    // Single-pass continuous memory sweep ensuring optimal cache efficiency
    for (int32 i = 0; i < POOL_SIZE_CEILING; ++i)
    {
        FLarvaAgentNode& Node = LarvaMemoryPool[i];
        if (!Node.bIsActive) continue;

        // Process physics: Hadamard-Rybczynski microscopic displacement logic
        Node.Position += Node.Velocity * DeltaTime;

        // Process biochemistry: Degrade yolk mass matrix over time steps
        Node.YolkReserveMm3 -= 0.0005f * DeltaTime;

        // Cull node if resources are completely exhausted
        if (Node.YolkReserveMm3 <= 0.0f)
        {
            Node.bIsActive = false;
            ActiveLarvaeCount--;
            // Pull pointer marker back if the cleared index is lower than the current head
            if (i < FirstAvailableIndex)
            {
                FirstAvailableIndex = i;
            }
        }
    }
}
