def main():
    for i in range(51):
        output_anomaly_graph = f"../data/anomaly/anomaly_{i}.png"
        with open(output_anomaly_graph.replace(".png", ".txt"), 'r') as anomaly_file:       
