import pin_utils
import qrcode

ipfs_link = "QmdY35fRPgUXC8S82VkJYEbbhYn6jFzozv23LijiidRDnx"
qrcode = pin_utils.create_ipfs_qr(ipfs_link)

pin_utils.print_thermal_txt("hello world")

pin_utils.print_thermal_img(qrcode)

