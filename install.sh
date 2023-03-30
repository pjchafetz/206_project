(return 0 2> /dev/null) && sourced=1 || sourced=0
if [ "$sourced" = 0 ]; then
    echo "Usage: ./install.sh"
    exit 1
fi

echo "Setting up virtual environment..."
python3 -m venv env
. env/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Done!"
