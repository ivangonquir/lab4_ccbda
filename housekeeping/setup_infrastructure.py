import os
import subprocess
from dotenv import dotenv_values

def run_command(command, check=False):
    """Runs a shell command and returns the output."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0 and check:
        print(f"Error executing command: {result.stderr}")
    return result.stdout.strip(), result.returncode

def start_backend(team_name):
    """Checks if Elastic Beanstalk is running, and starts it if it isn't."""
    print("\n--- 1. Checking Elastic Beanstalk Backend ---")
    os.chdir("elasticbeanstalk")
    
    # Check current status
    stdout, _ = run_command("eb status")
    
    if "Environment details for" in stdout:
        print(f"✅ Elastic Beanstalk environment '{team_name}' is already up and running!")
    else:
        print(f"⏳ Environment '{team_name}' is not running. Starting it now...")
        
        # Call the existing ebcreate.py script to generate the launch command
        launch_cmd, return_code = run_command(f"python ../ebcreate.py ../../.env.cloud {team_name}")
        
        if return_code == 0 and launch_cmd.startswith("eb create"):
            # Execute the generated 'eb create' command
            run_command(launch_cmd)
            print("✅ Elastic Beanstalk deployment initiated!")
        else:
            print("❌ Failed to generate the eb create command.")
            
    os.chdir("..")

def start_frontend():
    """Runs the frontend publishing script."""
    print("\n--- 2. Checking S3 and CloudFront Frontend ---")
    print("Executing publishFrontend.sh to ensure S3 and CloudFront are active...")
    
    # Run the bash script (assuming you updated it to be safe to run multiple times per Question 1)
    stdout, return_code = run_command("bash publishFrontend.sh")
    
    if return_code == 0:
        print("✅ Frontend deployment script executed successfully!")
    else:
        print("❌ Warning: Frontend script encountered an issue. Check your bash script.")

if __name__ == "__main__":
    print("Initializing Cloud Infrastructure...")
    
    # Load variables from .env.cloud
    config_path = "../.env.cloud"
    if not os.path.exists(config_path):
        print("❌ Error: .env.cloud file not found! Please create it in the root folder.")
        exit(1)
        
    config = dotenv_values(config_path)
    team_name = config.get("ELASTIC_BEANSTALK_ENV_NAME")
    
    if not team_name:
        print("❌ Error: ELASTIC_BEANSTALK_ENV_NAME is missing from .env.cloud")
        exit(1)

    start_backend(team_name)
    start_frontend()
    
    print("\n🎉 Infrastructure verification complete!")