{
    "Systemic_Circulation": {
        "Aortic_Hubs": {
            "Aortic_Arch": [
                {"Branch": "Brachiocephalic Trunk", "Destination": "Upper_Right_Limb_Head"},
                {"Branch": "Left Common Carotid Artery", "Destination": "Left_Head"},
                {"Branch": "Left Subclavian Artery", "Destination": "Left_Upper_Limb"}
            ],
            "Abdominal_Aorta": [
                {"Branch": "Celiac Trunk", "Destination": "Viscera_Superior"},
                {"Branch": "Superior Mesenteric Artery", "Destination": "GI_Small_Intestine"},
                {"Branch": "Renal Arteries", "Destination": "Kidneys"},
                {"Branch": "Inferior Mesenteric Artery", "Destination": "GI_Large_Intestine"},
                {"Branch": "Common Iliac Arteries", "Destination": "Pelvis_Lower_Limb"}
            ]
        },
        "Venous_Hubs": {
            "SVC_Tributaries": [
                {"Vein": "Brachiocephalic Veins (L&R)", "Source": "Upper_Limbs_Head_Neck"},
                {"Vein": "Azygos/Hemiazygos Veins", "Source": "Thorax_Spine"}
            ],
            "IVC_Tributaries": [
                {"Vein": "Hepatic Veins", "Source": "Liver"},
                {"Vein": "Renal Veins", "Source": "Kidneys"},
                {"Vein": "Common Iliac Veins", "Source": "Lower_Body"}
            ],
            "Portal_System": [
                {"Vein": "Splenic Vein", "Source": "Spleen_Pancreas"},
                {"Vein": "Superior/Inferior Mesenteric Veins", "Source": "GI_Tract"}
            ]
        }
    },
    
    "Metastasis_Sites": {
        "Solid_Organs": {
            "Liver": {
                "Arterial_Inflow": ["Common Hepatic Artery", "Hepatic Portal Vein (Vein Source)"],
                "Venous_Outflow": ["Hepatic Veins"],
                "Heart_Route": "IVC -> Right Atrium"
            },
            "Lungs": {
                "Arterial_Inflow": ["Bronchial Arteries"],
                "Venous_Outflow": ["Pulmonary Veins"],
                "Heart_Route": "Pulmonary Veins -> Left Atrium (Recirculation)"
            },
            "Kidneys": {
                "Arterial_Inflow": ["Renal Arteries"],
                "Venous_Outflow": ["Renal Veins"],
                "Heart_Route": "IVC -> Right Atrium"
            },
            "Brain": {
                "Arterial_Inflow": ["Internal Carotid Artery", "Vertebral Arteries"],
                "Venous_Outflow": ["Internal Jugular Veins (via Sinuses)"],
                "Heart_Route": "SVC -> Right Atrium"
            }
        },
        
        "Lymph_Nodes": {
            "Cervical_Nodes": {
                "Arterial_Supply": ["External Carotid Branches"],
                "Venous_Confluence": ["Internal Jugular Vein", "Subclavian Vein"],
                "Lymphatic_Trunk": "Jugular Trunk -> SVC"
            },
            "Axillary_Nodes": {
                "Arterial_Supply": ["Axillary Artery Branches"],
                "Venous_Confluence": ["Axillary Vein"],
                "Lymphatic_Trunk": "Subclavian Trunk -> SVC"
            }
        },
        
        "Bone_Sites": {
            "Femur": {
                "Arterial_Inflow": ["Medial Circumflex Femoral Artery"],
                "Venous_Outflow": ["Deep Femoral Veins"],
                "Heart_Route": "IVC -> Right Atrium"
            },
            "Vertebrae": {
                "Arterial_Inflow": ["Segmental Arteries (from Aorta)"],
                "Venous_Outflow": ["Vertebral Venous Plexus"],
                "Heart_Route": "SVC/IVC -> Right Atrium"
            }
        }
    }
}
