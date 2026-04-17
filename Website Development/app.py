from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-to-any-random-string"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "submissions.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS contact_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_date TEXT NOT NULL,
                comments TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/gallery")
def gallery():
    # These folders are where you’ll drop photos
    coffee_dir = BASE_DIR / "static" / "images" / "gallery" / "coffee"
    events_dir = BASE_DIR / "static" / "images" / "gallery" / "events"

    def list_images(folder: Path):
        if not folder.exists():
            return []
        exts = {".jpg", ".jpeg", ".png", ".webp"}
        files = [p for p in folder.iterdir() if p.suffix.lower() in exts]
        # Sort newest-first (optional)
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        # Convert to web paths
        return [f"images/gallery/{folder.name}/{p.name}" for p in files]

    coffee_images = list_images(coffee_dir)
    events_images = list_images(events_dir)

    return render_template(
        "gallery.html",
        coffee_images=coffee_images,
        events_images=events_images,
    )

from flask_mail import Mail, Message
import os

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)

from flask import request, jsonify, redirect, url_for, flash

@app.route("/contact", methods=["POST"])
def contact():
    first = (request.form.get("first_name") or "").strip()
    last = (request.form.get("last_name") or "").strip()
    email = (request.form.get("email") or "").strip()
    phone = (request.form.get("phone") or "").strip()
    event_type = (request.form.get("event_type") or "").strip()
    event_date = (request.form.get("event_date") or "").strip()
    comments = (request.form.get("comments") or "").strip()

    try:
        # 1) Email to Mazag
        inquiry_msg = Message(
            subject="New Inquiry",
            sender=app.config["MAIL_USERNAME"],
            recipients=["mazag.info@gmail.com"],
            reply_to=email if email else None,
        )

        inquiry_msg.body = f"""
New Inquiry Received

First Name: {first}
Last Name: {last}
Email: {email}
Phone: {phone}
Event Type: {event_type}
Event Date: {event_date}

Comments:
{comments if comments else "N/A"}
"""

        inquiry_msg.html = f"""
        <div style="font-family: Arial, Helvetica, sans-serif; line-height: 1.6; color: #2b2b2b; max-width: 640px; margin: 0 auto; padding: 24px;">
          <h2 style="margin: 0 0 18px; color: #6b4226;">New Inquiry</h2>

          <table cellpadding="0" cellspacing="0" border="0" style="width: 100%; border-collapse: collapse;">
            <tr>
              <td style="padding: 10px 0; border-bottom: 1px solid #e9dfd3; width: 160px;"><strong>First Name</strong></td>
              <td style="padding: 10px 0; border-bottom: 1px solid #e9dfd3;">{first}</td>
            </tr>
            <tr>
              <td style="padding: 10px 0; border-bottom: 1px solid #e9dfd3;"><strong>Last Name</strong></td>
              <td style="padding: 10px 0; border-bottom: 1px solid #e9dfd3;">{last}</td>
            </tr>
            <tr>
              <td style="padding: 10px 0; border-bottom: 1px solid #e9dfd3;"><strong>Email</strong></td>
              <td style="padding: 10px 0; border-bottom: 1px solid #e9dfd3;">{email}</td>
            </tr>
            <tr>
              <td style="padding: 10px 0; border-bottom: 1px solid #e9dfd3;"><strong>Phone</strong></td>
              <td style="padding: 10px 0; border-bottom: 1px solid #e9dfd3;">{phone}</td>
            </tr>
            <tr>
              <td style="padding: 10px 0; border-bottom: 1px solid #e9dfd3;"><strong>Event Type</strong></td>
              <td style="padding: 10px 0; border-bottom: 1px solid #e9dfd3;">{event_type}</td>
            </tr>
            <tr>
              <td style="padding: 10px 0; border-bottom: 1px solid #e9dfd3;"><strong>Event Date</strong></td>
              <td style="padding: 10px 0; border-bottom: 1px solid #e9dfd3;">{event_date}</td>
            </tr>
          </table>

          <div style="margin-top: 20px;">
            <p style="margin: 0 0 8px; color: #6b4226;"><strong>Comments</strong></p>
            <div style="background: #f2ebe2; border: 1px solid #e9dfd3; border-radius: 12px; padding: 14px;">
              {comments if comments else "N/A"}
            </div>
          </div>
        </div>
        """

        mail.send(inquiry_msg)

        # 2) Auto-reply to customer
        auto_reply = Message(
            subject="Mazag Coffee — We Received Your Inquiry ☕",
            sender=app.config["MAIL_USERNAME"],
            recipients=[email],
        )

        auto_reply.body = f"""
Hi {first},

We’re so glad you reached out.

We can’t wait to serve you at your special event, and we’re honored that you’ve chosen to work with Mazag.

We’ll follow up with you to confirm all the right details leading up to your event. Please allow up to 24 hours for a response.

Looking forward to creating something special with you.

– Mazag Coffee
mazag.info@gmail.com
(732)-668-1660
"""

        auto_reply.html = f"""
        <div style="margin:0; padding:0; background:#f2ebe2;">
          <div style="max-width:640px; margin:0 auto; padding:32px 24px; font-family: Arial, Helvetica, sans-serif; color:#2b2b2b; line-height:1.7;">
            <div style="background:rgba(255,255,255,0.65); border:1px solid #e9dfd3; border-radius:20px; padding:32px 28px; box-shadow:0 12px 30px rgba(0,0,0,0.06);">
              <div style="font-size:32px; font-weight:600; letter-spacing:0.3px; color:#6b4226; margin-bottom:8px;">
                Mazag
              </div>
              <div style="font-size:14px; color:#8a6a4f; margin-bottom:28px;">
                Coffee • Culture • Vibes
              </div>

              <p style="margin:0 0 16px;">Hi {first},</p>

              <p style="margin:0 0 16px;">
                We’re so glad you reached out.
              </p>

              <p style="margin:0 0 16px;">
                We can’t wait to serve you at your special event, and we’re honored that you’ve chosen to work with Mazag.
              </p>

              <p style="margin:0 0 16px;">
                Our team will review your request and follow up shortly to go over all the details.
                <strong>Please allow up to 24 hours for a response.</strong>
              </p>

              <p style="margin:0 0 24px;">
                Looking forward to creating something special with you.
              </p>

              <div style="padding-top:18px; border-top:1px solid #e9dfd3; color:#6b4226;">
                <div style="font-weight:600; margin-bottom:4px;">Mazag Coffee</div>
                <div><a href="mailto:mazag.info@gmail.com" style="color:#6b4226; text-decoration:none;">mazag.info@gmail.com</a></div>
                <div><a href="tel:+17326681660" style="color:#6b4226; text-decoration:none;">(732)-668-1660</a></div>
              </div>
            </div>
          </div>
        </div>
        """

        mail.send(auto_reply)

        # AJAX/fetch request
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"ok": True, "message": "Inquiry Sent!"})

        # Fallback normal form submit
        flash("Inquiry Sent!", "success")
        return redirect(url_for("home") + "#contact-us")

    except Exception as e:
        print("EMAIL ERROR:", e)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(
                {"ok": False, "message": "Something went wrong. Please try again."}
            ), 500

        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("home") + "#contact-us")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
