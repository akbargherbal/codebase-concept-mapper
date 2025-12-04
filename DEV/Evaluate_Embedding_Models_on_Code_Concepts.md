```python
# !rm -rf /content/codebase-concept-mapper/
```


```python
# Cell 1: Setup HuggingFace Token
# Go to: https://huggingface.co/settings/tokens
# Create a token, then add it to Colab secrets

from google.colab import userdata
from huggingface_hub import login

hf_token = userdata.get('HF_TOKEN')  # Add via left sidebar → 🔑 Secrets
login(token=hf_token)

# Also request access to gated model:
# Visit: https://huggingface.co/google/embeddinggemma-300m
# Click "Request Access" button
```


```python
# Cell 2: Clear GPU Memory
import torch
import gc

torch.cuda.empty_cache()
gc.collect()

print(f"GPU: {torch.cuda.get_device_properties(0).name}")
print(f"Total Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
print(f"Available Memory: {(torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)) / 1e9:.2f} GB")
```

    GPU: Tesla T4
    Total Memory: 15.83 GB
    Available Memory: 15.83 GB
    


```python
%%capture
# Suppress installation output
!pip install sentence-transformers torch numpy matplotlib

# Mount Google Drive for persistence
from google.colab import drive
drive.mount('/content/drive', force_remount=False)

print("✓ Dependencies installed")
print("✓ Google Drive mounted")
```


```python
import os
import shutil
from pathlib import Path

# Configuration
REPO_URL = "https://github.com/akbargherbal/codebase-concept-mapper.git"
REPO_NAME = "codebase-concept-mapper"
WORKING_DIR = f"/content/{REPO_NAME}/phase1"

def setup_repository():
    """Clone or sync the repository and navigate to working directory."""

    repo_path = Path(f"/content/{REPO_NAME}")

    # Check if repository already exists
    if repo_path.exists():
        print(f"✓ Repository '{REPO_NAME}' already exists")

        # Check if it's corrupted (common issue)
        try:
            os.chdir(repo_path)
            print("\n→ Syncing with remote...")

            # Fetch latest changes
            !git fetch origin

            # Show current branch and status
            !git branch --show-current
            !git status --short

            # Pull latest changes (assuming main branch, adjust if needed)
            print("\n→ Pulling latest changes...")
            !git pull origin main

        except (FileNotFoundError, OSError) as e:
            print(f"\n⚠️ Repository corrupted: {e}")
            print("🗑️ Removing and re-cloning...")

            # Go to safe directory first
            os.chdir('/content')

            # Force remove corrupted directory
            shutil.rmtree(repo_path, ignore_errors=True)

            # Clone fresh
            print(f"\n→ Cloning repository '{REPO_NAME}'...")
            !git clone {REPO_URL}
            print(f"✓ Repository cloned successfully")

    else:
        print(f"→ Cloning repository '{REPO_NAME}'...")
        os.chdir('/content')  # Make sure we're in a valid directory
        !git clone {REPO_URL}
        print(f"✓ Repository cloned successfully")

    # Verify structure
    print("\n" + "="*50)
    print("REPOSITORY STRUCTURE")
    print("="*50)

    # Check if tree command exists, otherwise use ls
    tree_check = !which tree
    if tree_check:
        !tree -L 2 {repo_path} -I '__pycache__|*.pyc|.git'
    else:
        print("(tree not installed, using ls)")
        !ls -la {repo_path}
        if Path(f"{repo_path}/phase1").exists():
            print(f"\nContents of phase1/:")
            !ls -la {repo_path}/phase1

    # Navigate to working directory
    working_path = Path(WORKING_DIR)
    if working_path.exists():
        os.chdir(WORKING_DIR)
        print(f"\n✓ Changed to working directory: {WORKING_DIR}")
        print(f"Current directory: {os.getcwd()}")

        # Show what's in the working directory
        print("\nFiles in working directory:")
        !ls -lh
    else:
        print(f"\n⚠️ Warning: '{WORKING_DIR}' does not exist")

        # Try to navigate to repo root at least
        try:
            os.chdir(repo_path)
            print(f"Staying in repo root: {os.getcwd()}")
            print("\nAvailable directories:")
            !ls -la
        except:
            print(f"Staying in: /content")
            os.chdir('/content')

# Run setup
setup_repository()
```

    → Cloning repository 'codebase-concept-mapper'...
    Cloning into 'codebase-concept-mapper'...
    remote: Enumerating objects: 57, done.[K
    remote: Counting objects: 100% (57/57), done.[K
    remote: Compressing objects: 100% (39/39), done.[K
    remote: Total 57 (delta 25), reused 49 (delta 17), pack-reused 0 (from 0)[K
    Receiving objects: 100% (57/57), 67.58 KiB | 13.51 MiB/s, done.
    Resolving deltas: 100% (25/25), done.
    ✓ Repository cloned successfully
    
    ==================================================
    REPOSITORY STRUCTURE
    ==================================================
    [01;34m/content/codebase-concept-mapper[0m
    ├── [01;34mdocs[0m
    │   ├── [00mCONTEXT.md[0m
    │   ├── [00mphase1_context.md[0m
    │   └── [00mPHASED_PLAN.md[0m
    ├── [01;34mphase1[0m
    │   ├── [00mall_results.json[0m
    │   ├── [00mcomparison.md[0m
    │   ├── [00mconcept_validators.py[0m
    │   ├── [00mdataset_generator.py[0m
    │   ├── [00mMODEL_RECOMMENDATIONS.md[0m
    │   ├── [00mproject_structure.md[0m
    │   ├── [00mQUICKSTART.md[0m
    │   ├── [00mREADME_PHASE1.md[0m
    │   ├── [00mresearch_query.md[0m
    │   ├── [00mresults_BAAI_bge-small-en-v1.5.json[0m
    │   ├── [00mresults_nomic-ai_CodeRankEmbed.json[0m
    │   ├── [00mresults_nomic-ai_nomic-embed-text-v1.5.json[0m
    │   ├── [01;32mrun_phase1.sh[0m
    │   ├── [01;32msetup_phase1.sh[0m
    │   └── [00mtest_embeddings.py[0m
    └── [00mrequirements.txt[0m
    
    2 directories, 19 files
    
    ✓ Changed to working directory: /content/codebase-concept-mapper/phase1
    Current directory: /content/codebase-concept-mapper/phase1
    
    Files in working directory:
    total 240K
    -rw-r--r-- 1 root root  61K Dec  4 07:22 all_results.json
    -rw-r--r-- 1 root root  636 Dec  4 07:22 comparison.md
    -rw-r--r-- 1 root root  12K Dec  4 07:22 concept_validators.py
    -rw-r--r-- 1 root root  12K Dec  4 07:22 dataset_generator.py
    -rw-r--r-- 1 root root 8.7K Dec  4 07:22 MODEL_RECOMMENDATIONS.md
    -rw-r--r-- 1 root root  13K Dec  4 07:22 project_structure.md
    -rw-r--r-- 1 root root  11K Dec  4 07:22 QUICKSTART.md
    -rw-r--r-- 1 root root 9.5K Dec  4 07:22 README_PHASE1.md
    -rw-r--r-- 1 root root 7.1K Dec  4 07:22 research_query.md
    -rw-r--r-- 1 root root  18K Dec  4 07:22 results_BAAI_bge-small-en-v1.5.json
    -rw-r--r-- 1 root root  18K Dec  4 07:22 results_nomic-ai_CodeRankEmbed.json
    -rw-r--r-- 1 root root  18K Dec  4 07:22 results_nomic-ai_nomic-embed-text-v1.5.json
    -rwxr-xr-x 1 root root 3.6K Dec  4 07:22 run_phase1.sh
    -rwxr-xr-x 1 root root 1.5K Dec  4 07:22 setup_phase1.sh
    -rw-r--r-- 1 root root  17K Dec  4 07:22 test_embeddings.py
    


```python

```


```python
%%capture
# Silent install (suppress output)
!pip install sentence-transformers torch numpy

print("✓ Dependencies installed")
```


```python
import torch

if torch.cuda.is_available():
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
else:
    print("⚠️  No GPU detected!")
    print("   Go to: Runtime > Change runtime type > Select T4 GPU")
```

    ✅ GPU: Tesla T4
       Memory: 15.8 GB
    


```python
from google.colab import drive

drive.mount('/content/drive')
print("✓ Google Drive mounted")
print("   Backups will be saved to: /content/drive/MyDrive/phase1_results_*")
```

    Drive already mounted at /content/drive; to attempt to forcibly remount, call drive.mount("/content/drive", force_remount=True).
    ✓ Google Drive mounted
       Backups will be saved to: /content/drive/MyDrive/phase1_results_*
    


```python
%%time
# Generate with Drive backup
!python dataset_generator.py

# Verify
import json
from pathlib import Path

if Path("test_code/metadata.json").exists():
    with open("test_code/metadata.json") as f:
        meta = json.load(f)
    print(f"\n✅ Dataset ready!")
    print(f"   Total: {meta['stats']['total_files']} files")
    print(f"   Python: {meta['stats']['python_files']}")
    print(f"   JavaScript: {meta['stats']['javascript_files']}")
else:
    print("❌ Generation failed - check errors above")
```

    
    ============================================================
    PHASE 1: GENERATING TEST DATASET (COLAB OPTIMIZED)
    ============================================================
    ✓ Created output directories in test_code
    
    📦 Processing PYTHON repositories...
    
      Repository: pallets/flask
      ✓ Cloned pallets/flask
      Found 12 candidate files
      Sampled 12 files
    
      Repository: psf/requests
      ✓ Cloned psf/requests
      Found 9 candidate files
      Sampled 9 files
    
      Repository: aio-libs/aiohttp
      ✓ Cloned aio-libs/aiohttp
      Found 28 candidate files
      Sampled 12 files
    
      Repository: django/django
      ✓ Cloned django/django
      Found 353 candidate files
      Sampled 12 files
    
      ✓ PYTHON: 45 files collected
    
    📦 Processing JAVASCRIPT repositories...
    
      Repository: axios/axios
      ✓ Cloned axios/axios
      Found 24 candidate files
      Sampled 12 files
    
      Repository: expressjs/express
      ✓ Cloned expressjs/express
      Found 3 candidate files
      Sampled 3 files
    
      Repository: facebook/react
      ✓ Cloned facebook/react
      Found 19 candidate files
      Sampled 12 files
    
      Repository: vercel/next.js
      ✓ Cloned vercel/next.js
      Found 520 candidate files
      Sampled 12 files
    
      ✓ JAVASCRIPT: 39 files collected
    
    ============================================================
    DATASET GENERATION COMPLETE
    ============================================================
    Total files: 84
    Python: 45
    JavaScript: 39
    Metadata saved to: test_code/metadata.json
    ============================================================
    
    
    ✅ Dataset ready!
       Total: 84 files
       Python: 45
       JavaScript: 39
    CPU times: user 71.4 ms, sys: 9.42 ms, total: 80.8 ms
    Wall time: 39.5 s
    


```python
%%time
# Test 3 candidate models
!python test_embeddings.py
```

    2025-12-04 07:23:40.532745: E external/local_xla/xla/stream_executor/cuda/cuda_fft.cc:467] Unable to register cuFFT factory: Attempting to register factory for plugin cuFFT when one has already been registered
    WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
    E0000 00:00:1764833020.571581    9063 cuda_dnn.cc:8579] Unable to register cuDNN factory: Attempting to register factory for plugin cuDNN when one has already been registered
    E0000 00:00:1764833020.581461    9063 cuda_blas.cc:1407] Unable to register cuBLAS factory: Attempting to register factory for plugin cuBLAS when one has already been registered
    W0000 00:00:1764833020.607183    9063 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
    W0000 00:00:1764833020.608066    9063 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
    W0000 00:00:1764833020.608089    9063 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
    W0000 00:00:1764833020.608097    9063 computation_placer.cc:177] computation placer already registered. Please check linkage and avoid linking the same target more than once.
    2025-12-04 07:23:40.615160: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
    To enable the following instructions: AVX2 AVX512F FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
    
    🔐 Setting up authentication...
    ⚠️ HuggingFace auth failed: 'NoneType' object has no attribute 'kernel'
    ✓ GPU detected: Tesla T4 (15.8 GB)
    
    📂 Loading test files...
      ✓ Loaded 84 files
    
    ✓ Ready to test on 84 files and 20 concepts
    
    
    ############################################################
    Loading model: Qwen/Qwen3-Embedding-0.6B
    ############################################################
      → Using trust_remote_code=True
      → Using torch.float16 for memory efficiency
    `torch_dtype` is deprecated! Use `dtype` instead!
    
    ============================================================
    Testing Model: Qwen/Qwen3-Embedding-0.6B
    Device: cuda
    ============================================================
    
    1️⃣ Embedding test files...
    Batches: 100% 11/11 [00:19<00:00,  1.73s/it]
      ✓ Embedded 84 files
    
    2️⃣ Testing concepts...
      ✗ context managers python                  P@5: 0.00 | P@1: 0
      ✗ async await python                       P@5: 0.20 | P@1: 0
      ✗ decorators python                        P@5: 0.40 | P@1: 0
      ✗ list comprehensions python               P@5: 0.20 | P@1: 0
      ✗ exception handling python                P@5: 0.40 | P@1: 1
      ✗ generators python                        P@5: 0.20 | P@1: 0
      ✓ class inheritance python                 P@5: 0.80 | P@1: 1
      ✗ file handling python                     P@5: 0.20 | P@1: 1
      ✗ lambda functions python                  P@5: 0.00 | P@1: 0
      ✗ dataclasses python                       P@5: 0.00 | P@1: 0
      ✗ promises javascript                      P@5: 0.40 | P@1: 1
      ✗ async await javascript                   P@5: 0.20 | P@1: 1
      ✗ react hooks                              P@5: 0.20 | P@1: 1
      ✗ closures javascript                      P@5: 0.20 | P@1: 1
      ✗ arrow functions javascript               P@5: 0.40 | P@1: 0
      ✗ destructuring javascript                 P@5: 0.00 | P@1: 0
      ✗ event handling javascript                P@5: 0.00 | P@1: 0
      ✗ callbacks javascript                     P@5: 0.00 | P@1: 0
      ✗ array methods javascript                 P@5: 0.40 | P@1: 1
      ✗ classes javascript                       P@5: 0.00 | P@1: 0
    
    ============================================================
    RESULTS SUMMARY
    ============================================================
    Overall Precision@5:  21.0%
    Overall Precision@1:  40.0%
    Mean Reciprocal Rank: 0.500
    Pass Rate (P@5≥60%): 5.0% (1/20)
    Inference Time:       20.5s
    Peak GPU Memory:      6.15 GB
    ============================================================
    
    💾 Results saved to results_Qwen_Qwen3-Embedding-0.6B.json
    
    
    ############################################################
    Loading model: intfloat/multilingual-e5-large-instruct
    ############################################################
      → Using torch.float16 for memory efficiency
    modules.json: 100% 349/349 [00:00<00:00, 2.84MB/s]
    config_sentence_transformers.json: 100% 128/128 [00:00<00:00, 820kB/s]
    README.md: 140kB [00:00, 48.2MB/s]
    sentence_xlm-roberta_config.json: 100% 53.0/53.0 [00:00<00:00, 423kB/s]
    config.json: 100% 690/690 [00:00<00:00, 5.38MB/s]
    model.safetensors: 100% 1.12G/1.12G [00:12<00:00, 90.6MB/s]
    tokenizer_config.json: 1.18kB [00:00, 5.78MB/s]
    sentencepiece.bpe.model: 100% 5.07M/5.07M [00:00<00:00, 8.88MB/s]
    tokenizer.json: 100% 17.1M/17.1M [00:00<00:00, 33.2MB/s]
    special_tokens_map.json: 100% 964/964 [00:00<00:00, 7.00MB/s]
    config.json: 100% 271/271 [00:00<00:00, 2.32MB/s]
    
    ============================================================
    Testing Model: intfloat/multilingual-e5-large-instruct
    Device: cuda
    ============================================================
    
    1️⃣ Embedding test files...
    Batches: 100% 11/11 [00:02<00:00,  4.78it/s]
      ✓ Embedded 84 files
    
    2️⃣ Testing concepts...
      ✗ context managers python                  P@5: 0.00 | P@1: 0
      ✓ async await python                       P@5: 0.60 | P@1: 1
      ✗ decorators python                        P@5: 0.20 | P@1: 0
      ✗ list comprehensions python               P@5: 0.40 | P@1: 0
      ✗ exception handling python                P@5: 0.40 | P@1: 0
      ✗ generators python                        P@5: 0.20 | P@1: 0
      ✓ class inheritance python                 P@5: 1.00 | P@1: 1
      ✗ file handling python                     P@5: 0.00 | P@1: 0
      ✗ lambda functions python                  P@5: 0.00 | P@1: 0
      ✗ dataclasses python                       P@5: 0.00 | P@1: 0
      ✗ promises javascript                      P@5: 0.20 | P@1: 0
      ✗ async await javascript                   P@5: 0.20 | P@1: 0
      ✗ react hooks                              P@5: 0.00 | P@1: 0
      ✗ closures javascript                      P@5: 0.40 | P@1: 0
      ✗ arrow functions javascript               P@5: 0.40 | P@1: 0
      ✗ destructuring javascript                 P@5: 0.00 | P@1: 0
      ✗ event handling javascript                P@5: 0.00 | P@1: 0
      ✗ callbacks javascript                     P@5: 0.00 | P@1: 0
      ✓ array methods javascript                 P@5: 0.60 | P@1: 1
      ✗ classes javascript                       P@5: 0.00 | P@1: 0
    
    ============================================================
    RESULTS SUMMARY
    ============================================================
    Overall Precision@5:  23.0%
    Overall Precision@1:  15.0%
    Mean Reciprocal Rank: 0.275
    Pass Rate (P@5≥60%): 15.0% (3/20)
    Inference Time:       3.2s
    Peak GPU Memory:      6.15 GB
    ============================================================
    
    💾 Results saved to results_intfloat_multilingual-e5-large-instruct.json
    
    
    ############################################################
    Loading model: google/embeddinggemma-300m
    ############################################################
      → Using torch.float16 for memory efficiency
    modules.json: 100% 573/573 [00:00<00:00, 4.63MB/s]
    config_sentence_transformers.json: 100% 997/997 [00:00<00:00, 8.66MB/s]
    README.md: 100% 18.7k/18.7k [00:00<00:00, 78.3MB/s]
    sentence_bert_config.json: 100% 58.0/58.0 [00:00<00:00, 474kB/s]
    config.json: 100% 1.49k/1.49k [00:00<00:00, 11.2MB/s]
    model.safetensors: 100% 1.21G/1.21G [00:08<00:00, 145MB/s]
    tokenizer_config.json: 100% 1.16M/1.16M [00:00<00:00, 2.65MB/s]
    tokenizer.model: 100% 4.69M/4.69M [00:00<00:00, 9.07MB/s]
    tokenizer.json: 100% 33.4M/33.4M [00:00<00:00, 64.4MB/s]
    added_tokens.json: 100% 35.0/35.0 [00:00<00:00, 283kB/s]
    special_tokens_map.json: 100% 662/662 [00:00<00:00, 4.46MB/s]
    config.json: 100% 312/312 [00:00<00:00, 2.11MB/s]
    config.json: 100% 134/134 [00:00<00:00, 1.02MB/s]
    2_Dense/model.safetensors: 100% 9.44M/9.44M [00:00<00:00, 18.5MB/s]
    config.json: 100% 134/134 [00:00<00:00, 956kB/s]
    3_Dense/model.safetensors: 100% 9.44M/9.44M [00:00<00:00, 17.6MB/s]
    
    ============================================================
    Testing Model: google/embeddinggemma-300m
    Device: cuda
    ============================================================
    
    1️⃣ Embedding test files...
    Batches: 100% 11/11 [00:07<00:00,  1.57it/s]
      ✓ Embedded 84 files
    
    2️⃣ Testing concepts...
      ✗ context managers python                  P@5: 0.00 | P@1: 0
      ✗ async await python                       P@5: 0.20 | P@1: 0
      ✗ decorators python                        P@5: 0.00 | P@1: 0
      ✗ list comprehensions python               P@5: 0.00 | P@1: 0
      ✓ exception handling python                P@5: 0.60 | P@1: 1
      ✗ generators python                        P@5: 0.00 | P@1: 0
      ✗ class inheritance python                 P@5: 0.40 | P@1: 0
      ✗ file handling python                     P@5: 0.20 | P@1: 0
      ✗ lambda functions python                  P@5: 0.00 | P@1: 0
      ✗ dataclasses python                       P@5: 0.00 | P@1: 0
      ✗ promises javascript                      P@5: 0.00 | P@1: 0
      ✗ async await javascript                   P@5: 0.00 | P@1: 0
      ✗ react hooks                              P@5: 0.00 | P@1: 0
      ✗ closures javascript                      P@5: 0.00 | P@1: 0
      ✗ arrow functions javascript               P@5: 0.00 | P@1: 0
      ✗ destructuring javascript                 P@5: 0.00 | P@1: 0
      ✗ event handling javascript                P@5: 0.00 | P@1: 0
      ✗ callbacks javascript                     P@5: 0.00 | P@1: 0
      ✗ array methods javascript                 P@5: 0.00 | P@1: 0
      ✗ classes javascript                       P@5: 0.00 | P@1: 0
    
    ============================================================
    RESULTS SUMMARY
    ============================================================
    Overall Precision@5:  7.0%
    Overall Precision@1:  5.0%
    Mean Reciprocal Rank: 0.104
    Pass Rate (P@5≥60%): 5.0% (1/20)
    Inference Time:       8.6s
    Peak GPU Memory:      6.15 GB
    ============================================================
    
    💾 Results saved to results_google_embeddinggemma-300m.json
    
    
    ############################################################
    Loading model: Alibaba-NLP/gte-multilingual-base
    ############################################################
      → Using trust_remote_code=True
      → Using torch.float16 for memory efficiency
    configuration.py: 7.13kB [00:00, 5.99MB/s]
    A new version of the following files was downloaded from https://huggingface.co/Alibaba-NLP/new-impl:
    - configuration.py
    . Make sure to double-check they do not contain any added malicious code. To avoid downloading new versions of the code file, you can pin a revision.
    modeling.py: 59.0kB [00:00, 34.9MB/s]
    A new version of the following files was downloaded from https://huggingface.co/Alibaba-NLP/new-impl:
    - modeling.py
    . Make sure to double-check they do not contain any added malicious code. To avoid downloading new versions of the code file, you can pin a revision.
    model.safetensors: 100% 611M/611M [00:10<00:00, 60.1MB/s]
    Some weights of the model checkpoint at Alibaba-NLP/gte-multilingual-base were not used when initializing NewModel: ['classifier.bias', 'classifier.weight']
    - This IS expected if you are initializing NewModel from the checkpoint of a model trained on another task or with another architecture (e.g. initializing a BertForSequenceClassification model from a BertForPreTraining model).
    - This IS NOT expected if you are initializing NewModel from the checkpoint of a model that you expect to be exactly identical (initializing a BertForSequenceClassification model from a BertForSequenceClassification model).
    tokenizer_config.json: 1.15kB [00:00, 4.67MB/s]
    tokenizer.json: 100% 17.1M/17.1M [00:00<00:00, 29.5MB/s]
    special_tokens_map.json: 100% 964/964 [00:00<00:00, 7.66MB/s]
    config.json: 100% 190/190 [00:00<00:00, 1.59MB/s]
    
    ============================================================
    Testing Model: Alibaba-NLP/gte-multilingual-base
    Device: cuda
    ============================================================
    
    1️⃣ Embedding test files...
    Batches: 100% 11/11 [00:05<00:00,  2.15it/s]
      ✓ Embedded 84 files
    
    2️⃣ Testing concepts...
      ✗ context managers python                  P@5: 0.00 | P@1: 0
      ✓ async await python                       P@5: 0.60 | P@1: 1
      ✗ decorators python                        P@5: 0.00 | P@1: 0
      ✗ list comprehensions python               P@5: 0.00 | P@1: 0
      ✓ exception handling python                P@5: 0.60 | P@1: 0
      ✗ generators python                        P@5: 0.20 | P@1: 0
      ✓ class inheritance python                 P@5: 0.80 | P@1: 1
      ✗ file handling python                     P@5: 0.20 | P@1: 0
      ✗ lambda functions python                  P@5: 0.00 | P@1: 0
      ✗ dataclasses python                       P@5: 0.00 | P@1: 0
      ✗ promises javascript                      P@5: 0.20 | P@1: 1
      ✗ async await javascript                   P@5: 0.20 | P@1: 0
      ✗ react hooks                              P@5: 0.40 | P@1: 1
      ✗ closures javascript                      P@5: 0.20 | P@1: 0
      ✗ arrow functions javascript               P@5: 0.20 | P@1: 0
      ✗ destructuring javascript                 P@5: 0.00 | P@1: 0
      ✗ event handling javascript                P@5: 0.40 | P@1: 1
      ✗ callbacks javascript                     P@5: 0.20 | P@1: 0
      ✓ array methods javascript                 P@5: 0.60 | P@1: 1
      ✗ classes javascript                       P@5: 0.20 | P@1: 0
    
    ============================================================
    RESULTS SUMMARY
    ============================================================
    Overall Precision@5:  25.0%
    Overall Precision@1:  30.0%
    Mean Reciprocal Rank: 0.458
    Pass Rate (P@5≥60%): 20.0% (4/20)
    Inference Time:       5.7s
    Peak GPU Memory:      6.15 GB
    ============================================================
    
    💾 Results saved to results_Alibaba-NLP_gte-multilingual-base.json
    
    
    
    ## Model Comparison
    
    | Model | P@5 | P@1 | MRR | Pass Rate | Time (s) | Device | Decision |
    |-------|-----|-----|-----|-----------|----------|--------|----------|
    | Alibaba-NLP/gte-multilingual-base | 25.0% | 30.0% | 0.458 | 20.0% | 5.7 | cuda | ❌ NO-GO |
    | intfloat/multilingual-e5-large-instruct | 23.0% | 15.0% | 0.275 | 15.0% | 3.2 | cuda | ❌ NO-GO |
    | Qwen/Qwen3-Embedding-0.6B | 21.0% | 40.0% | 0.500 | 5.0% | 20.5 | cuda | ❌ NO-GO |
    | google/embeddinggemma-300m | 7.0% | 5.0% | 0.104 | 5.0% | 8.6 | cuda | ❌ NO-GO |
    
    ### Recommendation
    
    **❌ STOP PROJECT** - Embedding approach not viable
    
    - Best model: `Alibaba-NLP/gte-multilingual-base` at 25.0% P@5
    - Threshold: ≥50% for conditional proceed
    - Recommendation: Consider alternative approaches or wait for better models
    
    
    💾 Comparison saved to comparison.md
    
    💾 Results saved to all_results.json
    CPU times: user 340 ms, sys: 59.4 ms, total: 400 ms
    Wall time: 2min 15s
    


```python
# Display comparison table
from IPython.display import Markdown, display

with open("comparison.md", "r") as f:
    display(Markdown(f.read()))
```



## Model Comparison

| Model | P@5 | P@1 | MRR | Pass Rate | Time (s) | Device | Decision |
|-------|-----|-----|-----|-----------|----------|--------|----------|
| Alibaba-NLP/gte-multilingual-base | 25.0% | 30.0% | 0.458 | 20.0% | 5.7 | cuda | ❌ NO-GO |
| intfloat/multilingual-e5-large-instruct | 23.0% | 15.0% | 0.275 | 15.0% | 3.2 | cuda | ❌ NO-GO |
| Qwen/Qwen3-Embedding-0.6B | 21.0% | 40.0% | 0.500 | 5.0% | 20.5 | cuda | ❌ NO-GO |
| google/embeddinggemma-300m | 7.0% | 5.0% | 0.104 | 5.0% | 8.6 | cuda | ❌ NO-GO |

### Recommendation

**❌ STOP PROJECT** - Embedding approach not viable

- Best model: `Alibaba-NLP/gte-multilingual-base` at 25.0% P@5
- Threshold: ≥50% for conditional proceed
- Recommendation: Consider alternative approaches or wait for better models




```python
import json

with open("all_results.json") as f:
    data = json.load(f)

models = [m for m in data["all_models"] if "error" not in m]
best = max(models, key=lambda x: x["overall_precision_at_5"])

print(f"🏆 Best Model: {best['model']}")
print(f"   P@5: {best['overall_precision_at_5']:.1%}")
print(f"   P@1: {best['overall_precision_at_1']:.1%}")
print(f"   Device: {best['device']}")

# Failed concepts
failed = [c for c in best['per_concept'] if c['precision_at_5'] < 0.6]
if failed:
    print(f"\n❌ Failed Concepts ({len(failed)}):")
    for c in failed[:5]:
        print(f"   - {c['concept']}")

# Top concepts
top = sorted(best['per_concept'], key=lambda x: x['precision_at_5'], reverse=True)[:5]
print(f"\n✅ Top Concepts:")
for c in top:
    print(f"   - {c['concept']}: {c['precision_at_5']:.2f}")
```

    🏆 Best Model: Alibaba-NLP/gte-multilingual-base
       P@5: 25.0%
       P@1: 30.0%
       Device: cuda
    
    ❌ Failed Concepts (16):
       - context managers python
       - decorators python
       - list comprehensions python
       - generators python
       - file handling python
    
    ✅ Top Concepts:
       - class inheritance python: 0.80
       - async await python: 0.60
       - exception handling python: 0.60
       - array methods javascript: 0.60
       - react hooks: 0.40
    


```python
import shutil
from pathlib import Path
from datetime import datetime

# Create timestamped backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path(f"/content/drive/MyDrive/phase1_results_{timestamp}")
backup_dir.mkdir(parents=True, exist_ok=True)

# Copy results
files_to_backup = [
    "all_results.json",
    "comparison.md",
    "test_code/metadata.json"
]

for f in files_to_backup:
    if Path(f).exists():
        shutil.copy(f, backup_dir / Path(f).name)

# Copy per-model results
for f in Path(".").glob("results_*.json"):
    shutil.copy(f, backup_dir / f.name)

print(f"✅ Backed up to: {backup_dir}")
print(f"\n📂 Files saved:")
for f in backup_dir.iterdir():
    print(f"   - {f.name}")
```

    ✅ Backed up to: /content/drive/MyDrive/phase1_results_20251204_072549
    
    📂 Files saved:
       - all_results.json
       - comparison.md
       - metadata.json
       - results_intfloat_multilingual-e5-large-instruct.json
       - results_Alibaba-NLP_gte-multilingual-base.json
       - results_nomic-ai_CodeRankEmbed.json
       - results_BAAI_bge-small-en-v1.5.json
       - results_Qwen_Qwen3-Embedding-0.6B.json
       - results_nomic-ai_nomic-embed-text-v1.5.json
       - results_google_embeddinggemma-300m.json
    


```python
# Save decision for Phase 2
with open("phase1_decision.txt", "w") as f:
    f.write(f"DECISION: GO TO PHASE 2\n")
    f.write(f"Model: {best['model']}\n")
    f.write(f"P@5: {best['overall_precision_at_5']:.1%}\n")

print("✅ Decision saved to phase1_decision.txt")
```

    ✅ Decision saved to phase1_decision.txt
    
