Setup:

virtualenv -p python3 venv
source ./venv/bin/activate
pip install -r requirements.txt
deactivate

OR

pip3 install -r requirements.txt


To Run:

source ./venv/bin/activate
python -m guacamole.xo.client
deactivate
