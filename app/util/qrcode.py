import qrcode
import base64
from io import BytesIO

class Qr:
    def __init__(this, data: str):
        qr = qrcode.QRCode(
            version = 1,
            error_correction = qrcode.constants.ERROR_CORRECT_L,
            box_size = 10,
            border = 1,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Create an image from the QR Code instance
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert image to base64 string
        buffered = BytesIO()
        # img.save(buffered, format="PNG") # format is not supported in python 3.9
        img.save(buffered)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        this.output = img_str
    
    def toHtmlTag(this):
        #data:image/png;base64
        return "data:image/png;base64," + this.output
    
    def base64_encoded(this):
        return this.output
