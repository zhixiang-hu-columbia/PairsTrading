echo you have to first set anaconda path to the system environment variable list... 

REM remove existing venv named pairsTradingEnv 
call conda env remove --name pairsTradingEnv -y 

REM create venv pairsTradingEnv 
call conda create -y --name pairsTradingEnv python=3.6 

REM enter venv 
call activate pairsTradingEnv 

REM install requirements 
python -m pip install -r requirements.txt 

echo "pairsTradingEnv virtual environment is ready." 

deactivate 

pause 