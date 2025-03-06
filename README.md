# The project for participation in Mielohackathon 2024
The goal of the hackathon was to improve one of suggested casual devices using ML/CV etc. We chose to enhance the properties of the refridgerator by adding external camera,
using which you can scan the food before putting it in, so it will be recognized, displayed and saved.
The code provides the example of how it can work, and it was even successfully carried out using computer web-camera.
We use barcode-scanner(CV), then we parse the data from the open database with barcodes and their descriptions.
The description is then preprocessed and added to the database.
