import configargparse
from utils.utils import generate_random_mac

parser = configargparse.get_argument_parser(
    name='default',
    formatter_class=configargparse.ArgumentDefaultsHelpFormatter
)

# --- Configuration files ---
parser.add_argument('--default-config', is_config_file=True, default='config/defaults.ini',
                    help='Default config file')

parser.add_argument('--log-level', type=str, default='INFO',help='Log level.')

parser.add_argument('--blink-config', is_config_file=True, required=False,
                    default='config/blink-defaults.ini', help='Blink request config file (optional).')

parser.add_argument('--cook-config', is_config_file=True, required=False,
                    default='config/cook-defaults.ini', help='Cook flow config file (optional).')

# --- Show Configuration ---
parser.add_argument('--show-config', type=bool, default=False,
                    help='Shows the current configuration if set to True.')

# -- Heart Beat ---
parser.add_argument('--heart-beat-interval', type=int, default=900,
                    help='The interval in seconds at which the emulator will send a HEARTBEAT event to maintain'
                         'its connection to mqtt')

# --- MQTT ---
parser.add_argument('--mqtt-broker', type=str, required=True, default='127.0.0.1',
                    help='Target MQTT broker IP.')

parser.add_argument('--mqtt-port', type=int, required=True, default=1883,
                    help='Target MQTT broker port.')

parser.add_argument('--mqtt-control-subscribe-topic', type=str, required=True, default='/iot/device/control',
                    help='MQTT Fire and Forget (F&F) subscription topic.')

parser.add_argument('--mqtt-control-publish-topic', type=str, required=True, default='/iot/client/control',
                    help='MQTT Fire and Forget (F&F) publish topic.')

parser.add_argument('--mqtt-workflow-subscribe-topic', type=str, required=True, default='/iot/device/workflow',
                    help='MQTT Workflow subscription topic.')

parser.add_argument('--mqtt-workflow-publish-topic', type=str, required=True, default='/iot/client/workflow',
                    help='MQTT Workflow publish topic.')

parser.add_argument('--mqtt-monitor-publish-topic', type=str, required=True, default='/iot/client/monitor',
                    help='MQTT Monitor publish topic.')

parser.add_argument('--mode', type=str, required=True, default='blink',
                    help='Emulation mode blink | cook.')

# --- Blink Flow ---
parser.add_argument('--blink-ack', type=int, default=1,
                    help='Number of blink ack payloads to send. MIN: 0 MAX: 3')

parser.add_argument('--blink-success', type=int, default=1,
                    help='Number of blink success payloads to send. MIN: 0 MAX: 3')

parser.add_argument('--blink-fail', type=int, default=0,
                    help='Number of blink fail payloads to send. MIN: 0 MAX: 3')

# --- Cook Flow ---
parser.add_argument('--cook-start', type=int, default=1,
                    help='Number of cook start payloads to send. MIN: 0 MAX: 3')

parser.add_argument('--cook-quantity', type=int, default=1,
                    help='Number of cook quantity payloads to send. MIN: 0 MAX: 3')

parser.add_argument('--cook-complete', type=int, default=1,
                    help='Number of cook complete payloads to send. MIN: 0 MAX: 3')

parser.add_argument('--cook-cancel', type=int, default=0,
                    help='Number of cook cancel payloads to send. MIN: 0 MAX: 3')

parser.add_argument('--cook-complete-ack', type=int, default=1,
                    help='Number of cook complete ack payloads to send. MIN: 0 MAX: 3')

parser.add_argument('--recipe-instance-id', type=int, default=1,
                    help='The recipe instance identifier.')

parser.add_argument('--recipe-name', type=str, default='OR Chicken',
                    help='The recipe name.')

parser.add_argument('--remaining-time', type=int, default='5',
                    help='The cook time for the current recipe.')

parser.add_argument('--product-quantity', type=int, default=1,
                    help='The product quantity to be cooked.')

parser.add_argument('--flow', type=str, default='"cook_start | cook_quantity | cook_complete | cook_complete_ack"',
                    help='The sequence of cook events to send to MQTT in any order separated by a pipe "|" character.'
                         'Valid input events: 1. cook_start 2. cook_quantity 3.'
                         'cook_complete 4. cook_cancel 5. cook_complete_ack')

# --- Emulation ---
parser.add_argument('--bezel-mac', type=str, default=generate_random_mac(),
                    help='Bezel mac address- will be generated randomly if not provided.')

parser.add_argument('--dest-mac', type=str, default=generate_random_mac(),
                    help='Destination mac address- will be generated randomly if not provided.')

parser.add_argument('--retry-interval', type=int, default=1,
                    help='Interval between sent response payloads within each iteration. Cannot be less than 0')

parser.add_argument('--loop-interval', type=int, default=1,
                    help='The period of time between loop iterations. Cannot be less than 0')

parser.add_argument('--loop', type=int, default=1,
                    help='How many times to run the given process. Cannot be less than 0')

cfg, unknown = parser.parse_known_args()
