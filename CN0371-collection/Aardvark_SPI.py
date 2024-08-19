"""
defs for data collection from the CN0371 board using Aardvark over SPI
"""

from aardvark_py import *

# Parameters
AARDVARK_SERIAL_ID = 2238652585
# -----------------
bitrate_khz = 500  # matches the clcock for 7192 clock speed adjusted for 2200 config
# -----------------
polarity = AA_SPI_POL_RISING_FALLING
# polarity = AA_SPI_POL_FALLING_RISING
# -----------------
phase = AA_SPI_PHASE_SAMPLE_SETUP
# phase = AA_SPI_PHASE_SETUP_SAMPLE
# -----------------
bitorder = AA_SPI_BITORDER_MSB
# bitorder = AA_SPI_BITORDER_LSB
# -----------------
ss_polarity = AA_SPI_SS_ACTIVE_LOW
# ss_polarity = AA_SPI_SS_ACTIVE_HIGH
# -----------------
target_power = AA_TARGET_POWER_BOTH  # enables pins providing power to the level shifter
# target_power = AA_TARGET_POWER_NONE
# -----------------------------------------------------------------------------

# Chip Select Masks for GPIO outputs
CS_7192 = 0x00
CS_2200 = 0x01


def aardvark_init():
    """
    Finds an opens port with the Aardvark
    -----------------

    """
    aa_devices_extended = aa_find_devices_ext(2, 2)
    #
    number_of_connected_aardvark = aa_devices_extended[0]
    print(aa_devices_extended)
    if number_of_connected_aardvark == 0:
        print("NO aardvark found")
        sys.exit(0)

    # Get the index of the port of the aardvark we want to control
    index_of_the_port = 0
    try:
        index_of_the_port = aa_devices_extended[2].index(AARDVARK_SERIAL_ID)
    except ValueError:
        print(f"Aardvark with serial id {AARDVARK_SERIAL_ID} not connected")
        sys.exit(0)

    # take the port of the first device found
    port_aardvark = aa_devices_extended[1][index_of_the_port]

    #
    aardvark_handle = aa_open(port_aardvark)
    print(f"open aardvark on port {port_aardvark}")
    if aardvark_handle < 0:
        print(f"error opening aardvark '{aa_status_string(aardvark_handle)}'")
        sys.exit(1)
    # aa_target_power(aardvark_handle, target_power)
    return aardvark_handle


def spi_CN0371_init(aardvark_handle):
    """
        configures and initializes SPI communication to CN0371 with Aardvark as the master
        sets I2C channels to GPIO for CS Extension
        Parameters
        ----------
        aardvark_handle: int
            port which aardvark is connected to

        Returns
        -------
        NONE
        """
    print(f"configure SPI")
    print(f"- bitrate {bitrate_khz}khz")
    if polarity == AA_SPI_POL_RISING_FALLING:
        print(f"- polarity falling")
    else:
        print(f"- polarity rising")

    if phase == AA_SPI_PHASE_SAMPLE_SETUP:
        print(f"- phase SAMPLE_SETUP")
    else:
        print(f"- phase SETUP_SAMPLE")

    if bitorder == AA_SPI_BITORDER_MSB:
        print(f"- phase MSB")
    else:
        print(f"- phase LSB")

    #
    aa_spi_bitrate(aardvark_handle, bitrate_khz)
    aa_spi_configure(aardvark_handle, polarity, phase, bitorder)

    # disable as slave
    aa_spi_slave_disable(aardvark_handle)

    #
    aa_spi_master_ss_polarity(aardvark_handle, ss_polarity)

    # Configure GPIO
    mask = 0x01  # GPIO Mask Select Bit for GPIO on SCL PIN
    aa_configure(aardvark_handle, AA_CONFIG_SPI_GPIO)
    aa_gpio_direction(aardvark_handle, mask)  # Sets output


def CN0371_configure(aardvark_handle):
    """
    """
    # Configure 7192


    aa_gpio_set(aardvark_handle, CS_7192)
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]), array('B'))
    if status < 0:
        print(f"fail sending data ({aa_status_string(status)})")
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x48, 0x00, 0x00, 0x00,]), array('B'))
    if status < 0:
        print(f"fail sending data ({aa_status_string(status)})")
    for i in range(3):
        status, data_in = aa_spi_write(aardvark_handle, array('B', [0x08, 0x0C, 0x00, 0x3F]), array('B'))
        if status < 0:
            print(f"fail sending data ({aa_status_string(status)})")
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x50, 0x00, 0x00, 0x00]), array('B'))
    if status < 0:
        print(f"fail sending data ({aa_status_string(status)})")
    for i in range(3):
        status, data_in = aa_spi_write(aardvark_handle, array('B', [0x10, 0x00, 0x01, 0x10]), array('B'))
        if status < 0:
            print(f"fail sending data ({aa_status_string(status)})")

    # Configure 2200
    aa_gpio_set(aardvark_handle, CS_2200)
    aa_spi_bitrate(aardvark_handle, 100)
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x00, 0x81]), array('B'))
    aa_sleep_ms(1000)  # wait for reset
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x00, 0x00]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x28, 0x00]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x29, 0x2D]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x2A, 0x08]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x2B, 0x06]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x2C, 0x01]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x11, 0x00]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x12, 0xA0]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x13, 0xC0]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x14, 0x0F]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x15, 0xC0]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x16, 0x0F]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x17, 0xC0]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x18, 0x0F]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x19, 0xC0]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x1A, 0x0F]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x1B, 0xC0]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x1C, 0x0F]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x1D, 0xC0]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x1E, 0x0F]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x1F, 0xC0]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x20, 0x0F]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x21, 0xC0]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x22, 0x0F]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x23, 0xC0]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x24, 0x0F]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x27, 0x00]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x10, 0x03]), array('B'))
    status, data_in = aa_spi_write(aardvark_handle, array('B', [0x00, 0x2A, 0x58]), array('B'))
    aa_spi_bitrate(aardvark_handle, bitrate_khz)

    aa_gpio_set(aardvark_handle, CS_7192)


# testing methods
"""handle = aardvark_init()
spi_master_init(handle)
CN0371_configure(handle)
aa_close(handle)"""






