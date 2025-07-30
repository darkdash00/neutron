from flask import Flask, request, send_file, render_template, redirect, url_for, flash
import yt_dlp
import os
import uuid

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    format_type = request.form.get('format')
    if not url:
        flash("Please provide a video or audio URL!")
        return redirect(url_for('index'))

    output_id = str(uuid.uuid4())
    filename_template = f"{output_id}.%(ext)s"
    download_folder = "downloads"
    os.makedirs(download_folder, exist_ok=True)

    ydl_opts = {
        'outtmpl': os.path.join(download_folder, filename_template),
        'quiet': True,
        'noprogress': True,
    }

    if format_type == 'mp3':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
        })
    else:
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4'
        })

    try:
        print(f"> Attempting download: URL={url}, format={format_type}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.download([url])
        # Finished, look for the new file(s)
        found_file = None
        for file in os.listdir(download_folder):
            if output_id in file:
                found_file = os.path.join(download_folder, file)
                break
        if not found_file:
            flash("No file was downloaded. The link may be invalid, private, or unsupported.")
            return redirect(url_for('index'))

        print(f"Download successful: {found_file}")
        return send_file(found_file, as_attachment=True)

    except Exception as e:
        print(f">> Download error: {e}")
        flash(f"Failed to download media. Error: {str(e)}")
        return redirect(url_for('index'))

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    app.run(debug=True)
