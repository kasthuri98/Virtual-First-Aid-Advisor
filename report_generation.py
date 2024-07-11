from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_first_aid_report(interaction_details, report_filename):
    c = canvas.Canvas(report_filename, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, height - 30, "First Aid Report")
    c.line(30, height - 40, width - 30, height - 40)

    # Timestamp
    c.setFont("Helvetica", 12)
    c.drawString(30, height - 70, f"Date and Time: {interaction_details['timestamp']}")

    # Location
    c.drawString(30, height - 100, f"Location: {interaction_details['location']}")

    # Emergency Contact
    c.drawString(30, height - 130, f"Emergency Contact: {'Yes' if interaction_details['emergency_contact'] else 'No'}")

    # Summary
    c.drawString(30, height - 160, "Summary:")
    text_object = c.beginText(30, height - 180)
    text_object.setFont("Helvetica", 12)
    for line in interaction_details['summary'].split('\n'):
        text_object.textLine(line)
    c.drawText(text_object)

    # First Aid Provided
    c.drawString(30, height - 250, "First Aid Provided:")
    text_object = c.beginText(30, height - 270)
    text_object.setFont("Helvetica", 12)
    for line in interaction_details['first_aid_provided'].split('\n'):
        text_object.textLine(line)
    c.drawText(text_object)

    c.showPage()
    c.save()

if __name__ == "__main__":
    # Example interaction details
    interaction_details = {
        "timestamp": "2024-06-27 10:15:00",
        "location": "123 Main St",
        "emergency_contact": True,
        "summary": "The user reported a minor burn and asked for first aid advice. The chatbot provided instructions on how to treat the burn.",
        "first_aid_provided": "1. Cool the burn under cool running water for at least 10 minutes.\n2. Apply aloe vera or a burn ointment to the affected area.\n3. Do not apply ice directly to the burn."
    }

    # Generate report
    report_filename = "first_aid_report.pdf"
    generate_first_aid_report(interaction_details, report_filename)
    print(f"Report generated: {report_filename}")
