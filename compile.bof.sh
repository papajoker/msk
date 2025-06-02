 #/usr/bin/env bash
 
nuitka main.py \
  --onefile \
  --output-dir=dist --output-filename=msk
    
# --onefile (10Mo)  : executable autonome / déplacable
# / --standalone (7Mo + lib Qt)
# sans aucun des 2 : 830ko  MAIS arbo src des .py doit exister