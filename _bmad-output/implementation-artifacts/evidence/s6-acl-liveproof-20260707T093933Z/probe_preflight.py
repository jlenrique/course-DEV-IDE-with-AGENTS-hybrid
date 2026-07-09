import os, sys
from pathlib import Path
REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
sys.path.insert(0, str(REPO)); os.chdir(REPO)
os.environ["PYTHONIOENCODING"]="utf-8"
os.environ.pop("OPENAI_API_KEY", None)
from dotenv import load_dotenv
load_dotenv(REPO/".env", override=True)
# prove default unset by exact name
disp_present = os.environ.get("MARCUS_RESEARCH_DISPATCH_LIVE") is not None
print("MARCUS_RESEARCH_DISPATCH_LIVE present-by-name:", disp_present, "value=", repr(os.environ.get("MARCUS_RESEARCH_DISPATCH_LIVE")))
key = os.environ.get("OPENAI_API_KEY","")
print("openai sk-:", key.startswith("sk-"), "subst-in-key:", "subst" in key)
print("GAMMA:", bool(os.environ.get("GAMMA_API_KEY")))
print("SCITE_ env keys:", [k for k in os.environ if k.startswith("SCITE")])
from app.marcus.orchestrator.production_runner import _research_dispatch_live
print("_research_dispatch_live():", _research_dispatch_live())
from app.marcus.orchestrator.research_wiring import _scite_creds_present
print("_scite_creds_present():", _scite_creds_present())
# bearer token file
sys.path.insert(0, str(REPO/"skills"/"bmad-agent-texas"/"scripts"))
from retrieval.scite_oauth_token import load_bearer_token, _token_path
print("token path:", _token_path(), "exists:", _token_path().exists())
tok = load_bearer_token()
print("bearer token present:", tok is not None, "len:", (len(tok) if tok else 0))
# corpus
corpus = REPO/"course-content/courses/tejal-apc-c1-m1-p2-trends"
print("corpus exists:", corpus.exists())
# provider directory
from retrieval.provider_directory import list_providers
ready = sorted(p.id for p in list_providers(shape="retrieval") if p.status in {"ready","stub"})
print("ready retrieval providers:", ready)
