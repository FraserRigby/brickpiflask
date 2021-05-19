# SPDX-FileCopyrightText: 2017 Scott Shawcroft  for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_motor.servo`
====================================================
Servos are motor based actuators that incorporate a feedback loop into the design. These feedback
loops enable pulse width modulated control to determine position or rotational speed.
* Author(s): Scott Shawcroft
"""

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Motor.git"

'''START SERVO CODE'''
# We disable the too few public methods check because this is a private base class for the two types
# of servos.
class _BaseServo:  # pylint: disable-msg=too-few-public-methods
    """Shared base class that handles pulse output based on a value between 0 and 1.0
    :param ~pwmio.PWMOut pwm_out: PWM output object.
    :param int min_pulse: The minimum pulse length of the servo in microseconds.
    :param int max_pulse: The maximum pulse length of the servo in microseconds."""

    def __init__(self, pwm_out, *, min_pulse=750, max_pulse=2250):
        self._pwm_out = pwm_out
        self._pwm_out.duty_cycle = 0
        self.set_pulse_width_range(min_pulse, max_pulse)

    def set_pulse_width_range(self, min_pulse=750, max_pulse=2250):
        """Change min and max pulse widths."""
        self._min_duty = int((min_pulse * self._pwm_out.frequency) / 1000000 * 0xFFFF)
        max_duty = (max_pulse * self._pwm_out.frequency) / 1000000 * 0xFFFF
        self._duty_range = int(max_duty - self._min_duty)

    @property
    def fraction(self):
        """Pulse width expressed as fraction between 0.0 (`min_pulse`) and 1.0 (`max_pulse`).
        For conventional servos, corresponds to the servo position as a fraction
        of the actuation range. Is None when servo is diabled (pulsewidth of 0ms).
        """
        if self._pwm_out.duty_cycle == 0:  # Special case for disabled servos
            return None
        return (self._pwm_out.duty_cycle - self._min_duty) / self._duty_range

    @fraction.setter
    def fraction(self, value):
        if value == 0:
            self._pwm_out.duty_cycle = 0  # disable the motor
            return
        if not 0.0 <= value <= 1.0:
            raise ValueError("Must be 0.0 to 1.0")
        print(value)
        duty_cycle = self._min_duty + int(value * self._duty_range)
        self._pwm_out.duty_cycle = duty_cycle


class Servo(_BaseServo):
    """Control the position of a servo.
       :param ~pwmio.PWMOut pwm_out: PWM output object.
       :param int actuation_range: The physical range of motion of the servo in degrees, \
           for the given ``min_pulse`` and ``max_pulse`` values.
       :param int min_pulse: The minimum pulse width of the servo in microseconds.
       :param int max_pulse: The maximum pulse width of the servo in microseconds.
       ``actuation_range`` is an exposed property and can be changed at any time:
        .. code-block:: python
          servo = Servo(pwm)
          servo.actuation_range = 135
       The specified pulse width range of a servo has historically been 1000-2000us,
       for a 90 degree range of motion. But nearly all modern servos have a 170-180
       degree range, and the pulse widths can go well out of the range to achieve this
       extended motion. The default values here of ``750`` and ``2250`` typically give
       135 degrees of motion. You can set ``actuation_range`` to correspond to the
       actual range of motion you observe with your given ``min_pulse`` and ``max_pulse``
       values.
       .. warning:: You can extend the pulse width above and below these limits to
         get a wider range of movement. But if you go too low or too high,
         the servo mechanism may hit the end stops, buzz, and draw extra current as it stalls.
         Test carefully to find the safe minimum and maximum.
    """

    def __init__(self, pwm_out, *, actuation_range=180, min_pulse=750, max_pulse= 2250):
        super().__init__(pwm_out, min_pulse=min_pulse, max_pulse=max_pulse)
        self.actuation_range = actuation_range
        """The physical range of motion of the servo in degrees."""
        self._pwm = pwm_out

    @property
    def angle(self):
        """The servo angle in degrees. Must be in the range ``0`` to ``actuation_range``.
        Is None when servo is disabled."""
        if self.fraction is None:  # special case for disabled servos
            return None
        return self.actuation_range * self.fraction

    @angle.setter
    def angle(self, new_angle):
        if new_angle is None:  # disable the servo by sending 0 signal
            self.fraction = None
            return
        if new_angle < 0 or new_angle > self.actuation_range:
            raise ValueError("Angle out of range")
        self.fraction = new_angle / self.actuation_range


#class ContinuousServo(_BaseServo):
    """Control a continuous rotation servo.
    :param int min_pulse: The minimum pulse width of the servo in microseconds.
    :param int max_pulse: The maximum pulse width of the servo in microseconds."""

    @property
    def throttle(self):
        """How much power is being delivered to the motor. Values range from ``-1.0`` (full
        throttle reverse) to ``1.0`` (full throttle forwards.) ``0`` will stop the motor from
        spinning."""
        return self.fraction

    @throttle.setter
    def throttle(self, value):
        if value > 1.0 or value < -1.0:
            raise ValueError("Throttle must be between -1.0 and 1.0")
        if value is None:
            raise ValueError("Continuous servos cannot spin freely")
        self.fraction = (value + 1) / 2

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.throttle = 0
'''END SERVO CODE'''

'''START PUMP CODE'''
class DCPump(_BaseServo):

    def __init__(self, pwm_out, *, min_pulse=750, max_pulse=5000):
        super().__init__(pwm_out, min_pulse=min_pulse, max_pulse=max_pulse)
        self._pwm = pwm_out

    @property
    def throttle(self):
        return self.fraction * 2 - 1

    @throttle.setter
    def throttle(self, value):
        if value <= 1.0 and value >= -1.0 and value != 0:
            self.fraction = value
        elif value is None or value == 0:
            self.fraction = 0
        else:
            raise ValueError("Throttle must be between -1.0 and 1.0")
            
    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.throttle = 0
'''END PUMP CODE'''

'''MOTOR CODE'''
'''#SPDX-FileCopyrightText: 2021 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_motor.motor`
====================================================
Simple control of a DC motor. DC motors have two wires and should not be connected directly to
the PWM connections. Instead use intermediate circuitry to control a much stronger power source with
the PWM. The `Adafruit Stepper + DC Motor FeatherWing <https://www.adafruit.com/product/2927>`_,
`Adafruit TB6612 1.2A DC/Stepper Motor Driver Breakout Board
<https://www.adafruit.com/product/2448>`_ and `Adafruit Motor/Stepper/Servo Shield for Arduino v2
Kit - v2.3 <https://www.adafruit.com/product/1438>`_ do this for popular form
factors already.
.. note:: The TB6612 boards feature three inputs XIN1, XIN2 and PWMX. Since we PWM the INs directly
  its expected that the PWM pin is consistently high.
* Author(s): Scott Shawcroft
"""

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Motor.git"

FAST_DECAY = 0
"""Recirculation current fast decay mode (coasting)"""

SLOW_DECAY = 1
"""Recirculation current slow decay mode (braking)"""


class DCMotor:
    """DC motor driver. ``positive_pwm`` and ``negative_pwm`` can be swapped if the motor runs in
    the opposite direction from what was expected for "forwards".
    Motor controller recirculation current decay mode is selectable and defaults to
    ``motor.FAST_DECAY`` (coasting). ``motor.SLOW_DECAY`` is recommended to improve spin
    threshold, speed-to-throttle linearity, and PWM frequency sensitivity.
    Decay mode settings only effect the operational performance of controller chips such
    as the DRV8833, DRV8871, and TB6612. Either decay mode setting is compatible
    with discrete h-bridge controller circuitry such as the L9110H and L293D; operational
    performance is not altered.
    :param ~pwmio.PWMOut positive_pwm: The motor input that causes the motor to spin forwards
      when high and the other is low.
    :param ~pwmio.PWMOut negative_pwm: The motor input that causes the motor to spin backwards
      when high and the other is low."""

    def __init__(self, positive_pwm, negative_pwm):
        self._positive = positive_pwm
        self._negative = negative_pwm
        self._throttle = 0
        self._decay_mode = FAST_DECAY

    @property
    def throttle(self):
        """Motor speed, ranging from -1.0 (full speed reverse) to 1.0 (full speed forward),
        or ``None`` (controller off).
        If ``None``, both PWMs are turned full off. If ``0.0``, both PWMs are turned full on.
        """
        return self._throttle

    @throttle.setter
    def throttle(self, value):
        if value is not None and (value > 1.0 or value < -1.0):
            raise ValueError("Throttle must be None or between -1.0 and +1.0")
        self._throttle = value
        if value is None:  # Turn off motor controller (high-Z)
            self._positive.duty_cycle = 0
            self._negative.duty_cycle = 0
        elif value == 0:  # Brake motor (low-Z)
            self._positive.duty_cycle = 0xFFFF
            self._negative.duty_cycle = 0xFFFF
        else:
            duty_cycle = int(0xFFFF * abs(value))
            if self._decay_mode == SLOW_DECAY:  # Slow Decay (Braking) Mode
                if value < 0:
                    self._positive.duty_cycle = 0xFFFF - duty_cycle
                    self._negative.duty_cycle = 0xFFFF
                else:
                    self._positive.duty_cycle = 0xFFFF
                    self._negative.duty_cycle = 0xFFFF - duty_cycle
            else:  # Default Fast Decay (Coasting) Mode
                if value < 0:
                    self._positive.duty_cycle = 0
                    self._negative.duty_cycle = duty_cycle
                else:
                    self._positive.duty_cycle = duty_cycle
                    self._negative.duty_cycle = 0

    @property
    def decay_mode(self):
        """Motor controller recirculation current decay mode. A value of ``motor.FAST_DECAY``
        sets the motor controller to the default fast recirculation current decay mode
        (coasting); ``motor.SLOW_DECAY`` sets slow decay (braking) mode."""
        return self._decay_mode

    @decay_mode.setter
    def decay_mode(self, mode=FAST_DECAY):
        if mode in (FAST_DECAY, SLOW_DECAY):
            self._decay_mode = mode
        else:
            raise ValueError(
                "Decay mode value must be either motor.FAST_DECAY or motor.SLOW_DECAY"
            )

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.throttle = None'''
'''END MOTOR CODE'''

'''START STEPPER CODE'''
'''# SPDX-FileCopyrightText: 2017 Scott Shawcroft  for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_motor.stepper`
====================================================
Stepper motors feature multiple wire coils that are used to rotate the magnets connected to the
motor shaft in a precise way. Each increment of the motor is called a step. Stepper motors have a
varying number of steps per rotation so check the motor's documentation to determine exactly how
precise each step is.
* Author(s): Tony DiCola, Scott Shawcroft
"""

import math

from micropython import const

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Motor.git"

# Stepper Motor Shield/Wing Driver
# Based on Adafruit Motorshield library:
# https://github.com/adafruit/Adafruit_Motor_Shield_V2_Library

# Constants that specify the direction and style of steps.
FORWARD = const(1)
"""Step forward"""
BACKWARD = const(2)
""""Step backward"""
SINGLE = const(1)
"""Step so that each step only activates a single coil"""
DOUBLE = const(2)
"""Step so that each step only activates two coils to produce more torque."""
INTERLEAVE = const(3)
"""Step half a step to alternate between single coil and double coil steps."""
MICROSTEP = const(4)
"""Step a fraction of a step by partially activating two neighboring coils. Step size is determined
   by ``microsteps`` constructor argument."""

_SINGLE_STEPS = bytes([0b0010, 0b0100, 0b0001, 0b1000])

_DOUBLE_STEPS = bytes([0b1010, 0b0110, 0b0101, 0b1001])

_INTERLEAVE_STEPS = bytes(
    [0b1010, 0b0010, 0b0110, 0b0100, 0b0101, 0b0001, 0b1001, 0b1000]
)


class StepperMotor:
    """A bipolar stepper motor or four coil unipolar motor. The use of microstepping requires
    pins that can output PWM. For non-microstepping, can set microsteps to None and use
    digital out pins.
    **PWM**
    :param ~pwmio.PWMOut ain1: `pwmio.PWMOut`-compatible output connected to the driver for
      the first coil (unipolar) or first input to first coil (bipolar).
    :param ~pwmio.PWMOut ain2: `pwmio.PWMOut`-compatible output connected to the driver for
      the third coil (unipolar) or second input to first coil (bipolar).
    :param ~pwmio.PWMOut bin1: `pwmio.PWMOut`-compatible output connected to the driver for
      the second coil (unipolar) or second input to second coil (bipolar).
    :param ~pwmio.PWMOut bin2: `pwmio.PWMOut`-compatible output connected to the driver for
      the fourth coil (unipolar) or second input to second coil (bipolar).
    :param int microsteps: Number of microsteps between full steps. Must be at least 2 and even.
    **Digital Out**
    :param ~digitalio.DigitalInOut ain1: `digitalio.DigitalInOut`-compatible output connected to
      the driver for the first coil (unipolar) or first input to first coil (bipolar).
    :param ~digitalio.DigitalInOut ain2: `digitalio.DigitalInOut`-compatible output connected to
      the driver for the third coil (unipolar) or second input to first coil (bipolar).
    :param ~digitalio.DigitalInOut bin1: `digitalio.DigitalInOut`-compatible output connected to
      the driver for the second coil (unipolar) or first input to second coil (bipolar).
    :param ~digitalio.DigitalInOut bin2: `digitalio.DigitalInOut`-compatible output connected to
      the driver for the fourth coil (unipolar) or second input to second coil (bipolar).
    :param microsteps: set to `None`
    """

    def __init__(self, ain1, ain2, bin1, bin2, *, microsteps=16):
        if microsteps is None:
            #
            # Digital IO Pins
            #
            self._steps = None
            self._coil = (ain1, ain2, bin1, bin2)
        else:
            #
            # PWM Pins
            #
            # set a safe pwm freq for each output
            self._coil = (ain2, bin1, ain1, bin2)
            for i in range(4):
                if self._coil[i].frequency < 1500:
                    self._coil[i].frequency = 2000
            if microsteps < 2:
                raise ValueError("Microsteps must be at least 2")
            if microsteps % 2 == 1:
                raise ValueError("Microsteps must be even")
            self._curve = [
                int(round(0xFFFF * math.sin(math.pi / (2 * microsteps) * i)))
                for i in range(microsteps + 1)
            ]
        self._current_microstep = 0
        self._microsteps = microsteps
        self._update_coils()

    def _update_coils(self, *, microstepping=False):
        if self._microsteps is None:
            #
            # Digital IO Pins
            #
            # Get coil activation sequence
            if self._steps is None:
                steps = 0b0000
            else:
                steps = self._steps[self._current_microstep % len(self._steps)]
            # Energize coils as appropriate:
            for i, coil in enumerate(self._coil):
                coil.value = (steps >> i) & 0x01
        else:
            #
            # PWM Pins
            #
            duty_cycles = [0, 0, 0, 0]
            trailing_coil = (self._current_microstep // self._microsteps) % 4
            leading_coil = (trailing_coil + 1) % 4
            microstep = self._current_microstep % self._microsteps
            duty_cycles[leading_coil] = self._curve[microstep]
            duty_cycles[trailing_coil] = self._curve[self._microsteps - microstep]

            # This ensures DOUBLE steps use full torque. Without it, we'd use
            #  partial torque from the microstepping curve (0xb504).
            if not microstepping and (
                duty_cycles[leading_coil] == duty_cycles[trailing_coil]
                and duty_cycles[leading_coil] > 0
            ):
                duty_cycles[leading_coil] = 0xFFFF
                duty_cycles[trailing_coil] = 0xFFFF

            # Energize coils as appropriate:
            for i in range(4):
                self._coil[i].duty_cycle = duty_cycles[i]

    def release(self):
        """Releases all the coils so the motor can free spin, also won't use any power"""
        # De-energize coils:
        for coil in self._coil:
            if self._microsteps is None:
                coil.value = 0
            else:
                coil.duty_cycle = 0

    def onestep(
        self, *, direction=FORWARD, style=SINGLE
    ):  # pylint: disable=too-many-branches
        """Performs one step of a particular style. The actual rotation amount will vary by style.
        `SINGLE` and `DOUBLE` will normal cause a full step rotation. `INTERLEAVE` will normally
        do a half step rotation. `MICROSTEP` will perform the smallest configured step.
        When step styles are mixed, subsequent `SINGLE`, `DOUBLE` or `INTERLEAVE` steps may be
        less than normal in order to align to the desired style's pattern.
        :param int direction: Either `FORWARD` or `BACKWARD`
        :param int style: `SINGLE`, `DOUBLE`, `INTERLEAVE`"""
        if self._microsteps is None:
            #
            # Digital IO Pins
            #
            step_size = 1
            if style == SINGLE:
                self._steps = _SINGLE_STEPS
            elif style == DOUBLE:
                self._steps = _DOUBLE_STEPS
            elif style == INTERLEAVE:
                self._steps = _INTERLEAVE_STEPS
            else:
                raise ValueError("Unsupported step style.")
        else:
            #
            # PWM Pins
            #
            # Adjust current steps based on the direction and type of step.
            step_size = 0
            if style == MICROSTEP:
                step_size = 1
            else:
                half_step = self._microsteps // 2
                full_step = self._microsteps
                # Its possible the previous steps were MICROSTEPS so first align
                #  with the interleave pattern.
                additional_microsteps = self._current_microstep % half_step
                if additional_microsteps != 0:
                    # We set _current_microstep directly because our step size varies
                    # depending on the direction.
                    if direction == FORWARD:
                        self._current_microstep += half_step - additional_microsteps
                    else:
                        self._current_microstep -= additional_microsteps
                    step_size = 0
                elif style == INTERLEAVE:
                    step_size = half_step

                current_interleave = self._current_microstep // half_step
                if (style == SINGLE and current_interleave % 2 == 1) or (
                    style == DOUBLE and current_interleave % 2 == 0
                ):
                    step_size = half_step
                elif style in (SINGLE, DOUBLE):
                    step_size = full_step

        if direction == FORWARD:
            self._current_microstep += step_size
        else:
            self._current_microstep -= step_size

        # Now that we know our target microstep we can determine how to energize the four coils.
        self._update_coils(microstepping=style == MICROSTEP)

        return self._current_microstep'''
'''END STEPPER CODE'''