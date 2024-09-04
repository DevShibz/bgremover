from flask import Flask, request, send_file, make_response, render_template_string
from flask_cors import CORS
from rembg import remove
from PIL import Image
import io

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

def remove_background(input_image):
    # Remove the background
    output_image = remove(input_image)
    return output_image

@app.route('/remove_background', methods=['POST'])
def api_remove_background():
    if 'image' not in request.files:
        return 'No image file provided', 400
    
    file = request.files['image']
    
    # Process the image
    input_image = Image.open(file.stream)
    output_image = remove_background(input_image)
    
    # Save the output image to a byte stream
    img_byte_arr = io.BytesIO()
    output_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    # Create response with file download headers
    response = make_response(send_file(img_byte_arr, mimetype='image/png'))
    response.headers['Content-Disposition'] = 'attachment; filename=processed_image.png'
    return response

@app.route('/')
def index():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Background Remover</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
        <style>
            body {
                background-color: #f8f9fa;
            }
            .container {
                max-width: 800px;
            }
            .card {
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            #preview {
                max-width: 100%;
                max-height: 400px;
                object-fit: contain;
            }
            .btn-file {
                position: relative;
                overflow: hidden;
            }
            .btn-file input[type=file] {
                position: absolute;
                top: 0;
                right: 0;
                min-width: 100%;
                min-height: 100%;
                font-size: 100px;
                text-align: right;
                filter: alpha(opacity=0);
                opacity: 0;
                outline: none;
                background: white;
                cursor: inherit;
                display: block;
            }
        </style>
    </head>
    <body>
        <div class="container mt-5">
            <div class="card p-4">
                <h1 class="text-center mb-4">Background Remover</h1>
                <div class="mb-3">
                    <div class="d-grid">
                        <span class="btn btn-primary btn-file">
                            <i class="fas fa-upload me-2"></i>Choose Image
                            <input type="file" id="imageUpload" accept="image/*">
                        </span>
                    </div>
                </div>
                <div class="mb-3 d-grid">
                    <button id="processButton" class="btn btn-success" disabled>
                        <i class="fas fa-magic me-2"></i>Remove Background
                    </button>
                </div>
                <div id="previewContainer" class="mb-3 d-none">
                    <h3 class="text-center">Preview</h3>
                    <div class="text-center">
                        <img id="preview" src="" alt="Preview" class="img-fluid rounded">
                    </div>
                </div>
                <div id="downloadContainer" class="d-none d-grid">
                    <a id="downloadLink" class="btn btn-primary" download="processed_image.png">
                        <i class="fas fa-download me-2"></i>Download Processed Image
                    </a>
                </div>
            </div>
        </div>

        <script>
            const imageUpload = document.getElementById('imageUpload');
            const processButton = document.getElementById('processButton');
            const preview = document.getElementById('preview');
            const previewContainer = document.getElementById('previewContainer');
            const downloadContainer = document.getElementById('downloadContainer');
            const downloadLink = document.getElementById('downloadLink');

            imageUpload.addEventListener('change', function(e) {
                if (e.target.files.length > 0) {
                    processButton.disabled = false;
                    const file = e.target.files[0];
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        preview.src = e.target.result;
                        previewContainer.classList.remove('d-none');
                    }
                    reader.readAsDataURL(file);
                } else {
                    processButton.disabled = true;
                    previewContainer.classList.add('d-none');
                }
            });

            processButton.addEventListener('click', function() {
                const formData = new FormData();
                formData.append('image', imageUpload.files[0]);

                processButton.disabled = true;
                processButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';

                fetch('/remove_background', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.blob())
                .then(blob => {
                    const url = URL.createObjectURL(blob);
                    preview.src = url;
                    downloadLink.href = url;
                    downloadContainer.classList.remove('d-none');
                    processButton.innerHTML = '<i class="fas fa-magic me-2"></i>Remove Background';
                    processButton.disabled = false;
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while processing the image.');
                    processButton.innerHTML = '<i class="fas fa-magic me-2"></i>Remove Background';
                    processButton.disabled = false;
                });
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == '__main__':
    app.run(debug=True)