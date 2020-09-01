import json
from enum import Enum
import matplotlib.pyplot as plt


def create_comma_separated_string(some_list):
    comma_separated = ""
    for element in some_list:
        comma_separated += str(element) + ","
    return comma_separated


def comma_separated_durations(resultfile='result.json', key_name="activationListEntry", limit=-1):
    comma_separated_durations = []
    try:
        with open(resultfile) as json_file:
            result = json.load(json_file)
    except:
        pass

    for i in range(0, len(result.keys())):
        limit_check = (not result[str(i)][key_name]["duration"] > limit) if limit > 0 else True
        if limit_check:
            comma_separated_durations.append(result[str(i)][key_name]["duration"])
    comma_separated_durations.sort()
    # print("path: {} | List: {}".format(resultfile, create_comma_separated_string(comma_separated_durations)))
    return comma_separated_durations


def timestamp_as_number(timestamped_object):
    timestamp = timestamped_object.get("timestamp")
    timestamp = timestamp.replace("-", "")
    timestamp = timestamp.replace("T", "")
    timestamp = timestamp.replace(":", "")
    timestamp = timestamp.replace("Z", "")
    return float(timestamp)


def extract_values(object_list):
    values = []
    for element in object_list:
        values.append(element.get("value"))
    return values


def get_metrics(filter_key_list, file='result.json', endpoints_to_check=None):
    if endpoints_to_check is None:
        endpoints_to_check = [1]
    try:
        with open(file) as json_file:
            metrics = json.load(json_file)
    except:
        print("File not found")
        return

    value_list = []
    endpoint_counter = 0
    for endpoint in metrics.keys():
        if endpoint_counter in endpoints_to_check:
            print(endpoint)
            for timestamp in metrics.get(endpoint).keys():
                metric_list = metrics.get(endpoint).get(timestamp)
                for metric_entry in metric_list:
                    metric_name = metric_entry.split(" ")[0]
                    metric_value = metric_entry.split(" ")[1]
                    constraint = True

                    for key in filter_key_list:
                        if key == "node_load1" or key == "node_load15":
                            constraint = constraint and (key == metric_name)
                        else:
                            constraint = key in metric_name

                    if constraint:
                        # print("name {} - value {}".format(metric_name, metric_value))
                        value_list.append({"timestamp": timestamp, "value": float(metric_value)})
                        # value_list.append(float(metric_value))
        endpoint_counter += 1
    value_list.sort(key=timestamp_as_number)
    print(create_comma_separated_string(extract_values(value_list)))
    return extract_values(value_list)


def evaluate_results(paths, name):
    print(name)
    result = []
    for i in range(0, len(paths)):
        result.extend(comma_separated_durations(paths[i]))
    result.sort()
    print("Processed a total of {} elements".format(len(result)))
    print(create_comma_separated_string(result) + "\n\n")
    return result


class Experiment(Enum):
    PROVIDER = "provider_side"
    FUNCTION = "function_side"
    BASELINE = "baseline"


def print_result(experiment_type=Experiment.PROVIDER):
    print("{} RESULTS \n\nProductUpdate:".format(experiment_type.value))
    print(create_comma_separated_string(
        comma_separated_durations("provider_side_result.json", key_name="activationListEntry")))
    print("\nFetchImagesAction:")
    print(create_comma_separated_string(
        comma_separated_durations("fetchImages_{}_result.json".format(experiment_type.value),
                                  key_name="fetchImagesActionEntry")))
    print("\n________________________________\n")


def all_results_printer():
    print_result(Experiment.PROVIDER)
    print_result(Experiment.FUNCTION)
    print_result(Experiment.BASELINE)


def plot_maker(metrics, title="", y_axis=""):
    plt.plot(metrics)
    plt.title(title)
    plt.ylabel(y_axis)
    plt.show()


def box_plot_maker(title, key_specifier, metrics_provider, metrics_function, metrics_baseline):
    data = [metrics_provider, metrics_function, metrics_baseline]
    plt.boxplot(data, 0, '')
    plt.title(title)
    plt.ylabel(key_specifier)
    plt.show()


def metric_caller(key_specifier, endpoints):
    metrics_provider = get_metrics(filter_key_list=[key_specifier], file="provider_side_ow_logs.json", endpoints_to_check=endpoints)
    metrics_function = get_metrics(filter_key_list=[key_specifier], file="function_side_ow_logs.json", endpoints_to_check=endpoints)
    metrics_baseline = get_metrics(filter_key_list=[key_specifier], file="baseline_ow_logs.json", endpoints_to_check=endpoints)
    plot_maker(metrics_provider, Experiment.PROVIDER.name, key_specifier)
    plot_maker(metrics_function, Experiment.FUNCTION.name, key_specifier)
    plot_maker(metrics_baseline, Experiment.BASELINE.name, key_specifier)
    box_plot_maker("1:{}, 2:{}, 3:{}".format(Experiment.PROVIDER.name, Experiment.FUNCTION.name, Experiment.BASELINE.name), key_specifier, metrics_provider, metrics_function, metrics_baseline)


# Visualize
"""
# HELP node_cpu Seconds the cpus spent in each mode
# HELP node_memory_Active Memory information field Active.
# HELP node_disk_io_now The number of I/Os currently in progress.
# HELP node_load1 1m load average.
# HELP node_memory_MemFree Memory information field MemFree.
# HELP node_memory_MemTotal Memory information field MemTotal
node_network_receive_bytes
node_network_transmit_bytes
"""
if __name__ == '__main__':
    all_results_printer()
    metric_caller(key_specifier="node_network_transmit_bytes", endpoints=[3])

#2
