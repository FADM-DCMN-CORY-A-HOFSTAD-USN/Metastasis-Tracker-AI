import os
import json
import time
import uuid
import requests
import jwt  # Requires: pip install PyJWT cryptography

class EpicInterconnectGateway:
    """
    Manages secure transmission of Metastasis-Tracker FHIR payloads into 
    Epic EHR systems using SMART on FHIR Backend Services authorization.
    """
    def __init__(self, epic_base_url: str, client_id: str, private_key_path: str):
        self.epic_fhir_url = f"{epic_base_url}/api/FHIR/R4"
        self.epic_token_url = f"{epic_base_url}/oauth2/token"
        self.client_id = client_id
        
        # Load the private key registered with Epic Connection Hub
        with open(private_key_path, 'r') as key_file:
            self.private_key = key_file.read()

    def _generate_client_assertion(self) -> str:
        """
        Generates an RS384 signed JWT to prove the identity of the AI suite to Epic.
        """
        now = int(time.time())
        payload = {
            "iss": self.client_id,
            "sub": self.client_id,
            "aud": self.epic_token_url,
            "jti": str(uuid.uuid4()),
            "exp": now + 300, # Token expires in 5 minutes
            "iat": now
        }
        
        # Sign the token using our private SSL key
        token = jwt.encode(payload, self.private_key, algorithm="RS384")
        return token

    def authenticate_with_epic(self) -> str:
        """
        Exchanges the signed JWT for a live Epic Access Token.
        """
        print(f"[*] Initiating SMART on FHIR Handshake with Epic Interconnect...")
        assertion = self._generate_client_assertion()
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": assertion
        }
        
        response = requests.post(self.epic_token_url, headers=headers, data=data)
        
        if response.status_code == 200:
            print("[+] Epic Authentication Successful. Secure channel established.")
            return response.json().get('access_token')
        else:
            raise PermissionError(f"Epic Auth Failed [{response.status_code}]: {response.text}")

    def transmit_metastasis_bundle(self, fhir_bundle_path: str) -> bool:
        """
        Transmits the generated FHIR transaction bundle directly to Epic.
        """
        access_token = self.authenticate_with_epic()
        
        with open(fhir_bundle_path, 'r') as f:
            bundle_payload = json.load(f)

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json"
        }
        
        print(f"[*] Pushing diagnostic bundle to Epic Chronicles Database...")
        # POST to the base FHIR endpoint to process the Transaction Bundle
        response = requests.post(self.epic_fhir_url, headers=headers, json=bundle_payload)
        
        if response.status_code in [200, 201]:
            print(f"[+] SUCCESS: Payload accepted by Epic. Patient chart updated.")
            return True
        else:
            print(f"[-] EPIC REJECTION [{response.status_code}]: {response.text}")
            return False

if __name__ == "__main__":
    # Integration Sandbox Testing
    gateway = EpicInterconnectGateway(
        epic_base_url="https://epicproxy.hospital.org/interconnect-prd",
        client_id="metastasis-tracker-prod-uuid",
        private_key_path="workspace/certs/epic_private.pem"
    )
    # gateway.transmit_metastasis_bundle("outbound/EHR-2026-9904_metastasis_bundle.json")
