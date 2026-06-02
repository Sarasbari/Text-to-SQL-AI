import os
import argparse
from huggingface_hub import HfApi, create_repo

def push_to_hub(adapter_dir: str, repo_id: str, token: str | None = None):
    hf_token = token or os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError("Hugging Face API token must be provided via argument or HF_TOKEN environment variable.")
        
    print(f"Authenticating with Hugging Face Hub...")
    api = HfApi(token=hf_token)
    
    print(f"Creating/verifying Hugging Face repository {repo_id}...")
    try:
        create_repo(
            repo_id=repo_id,
            token=hf_token,
            private=True, # default to private repository for custom model adapter weights
            exist_ok=True
        )
        print(f"Repository {repo_id} ready.")
    except Exception as e:
        print(f"Note: Repository creation checked, proceeding. Details: {e}")
        
    print(f"Uploading adapter folder '{adapter_dir}' to Hugging Face repository '{repo_id}'...")
    try:
        api.upload_folder(
            folder_path=adapter_dir,
            repo_id=repo_id,
            repo_type="model"
        )
        print("Upload completed successfully! Your model adapter is live on Hugging Face Hub.")
    except Exception as e:
        print(f"Error uploading adapter weights to hub: {e}")
        raise e

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Push fine-tuned LoRA adapter to Hugging Face Hub.")
    parser.add_argument("--adapter_dir", type=str, required=True, help="Path to local folder containing adapter weights")
    parser.add_argument("--repo_id", type=str, required=True, help="Hugging Face Repository ID (e.g. username/sqlcoder-adapter)")
    parser.add_argument("--token", type=str, default=None, help="Hugging Face User Access Token (optional, falls back to env variable)")
    
    args = parser.parse_args()
    push_to_hub(args.adapter_dir, args.repo_id, args.token)
