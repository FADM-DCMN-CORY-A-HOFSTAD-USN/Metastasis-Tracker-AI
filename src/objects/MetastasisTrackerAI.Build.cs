using UnrealBuildTool;

public class MetastasisTrackerAI : ModuleRules
{
    public MetastasisTrackerAI(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
	
        // Core framework execution modules
        PublicDependencyModuleNames.AddRange(new string[] { 
            "Core", 
            "CoreUObject", 
            "Engine", 
            "InputCore" 
        });

        // CRITICAL: Explicitly mount the rigid-body and sub-stepping subsystems
        PrivateDependencyModuleNames.AddRange(new string[] { 
            "PhysicsCore"
        });
        
        // Optimize command line compiling speed by omitting heavy editor references
        if (Target.Type == TargetRules.TargetType.Server || Target.Configuration == UnrealTargetConfiguration.Debug)
        {
            bUseUnityBuild = false; // Disable unity builds to simplify compiler log isolation
        }
    }
}
