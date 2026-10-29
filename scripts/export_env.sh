#!/usr/bin/env bash
# Usage : ./scripts/export_env.sh "message du commit"
# À lancer avec l'environnement activé, depuis la racine du projet.
set -euo pipefail
mkdir -p envs
conda env export --no-builds > envs/env_busco.yml 2>/dev/null
{
  echo "Date : $(date)"
  echo "BUSCO : $(busco --version)"
  echo "datasets : $(datasets --version)"
  echo "Python : $(python --version 2>&1)"
  echo; conda list
} > envs/versions.txt
git add envs/env_busco.yml
git commit -m "envs: ${1:-mise à jour de l'environnement}"
echo "Exporté et commité. Pensez à : git push"
