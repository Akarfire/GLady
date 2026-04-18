from pathlib import Path

def generate_requirements(file_path : str, directories : list[str]):
    
    # This will be written into file_path
    requirements : list[str] = []    
    
    for dir in directories:
        path : Path = Path(dir)
        if not path.exists(): continue
        
        requirement_files = [file for file in path.rglob("requirements.txt") if file.is_file()]
        for req_file in requirement_files:
            with req_file.open('r') as rf:
                lines = rf.readlines()
                requirements.extend(lines)
                
    # Writing gathered requirements into a file
    with open(file_path, 'w') as f:
        for req in requirements:
            f.write(req + "\n")
    

# Script RUN FROM GLady directory!
if __name__ == "__main__":
    generate_requirements("./requirements_gen.txt", ["./Source", "./Plugins"])                
    