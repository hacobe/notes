"""ThreadPoolExecutor example.

Sources:
* https://github.com/openai/human-eval/blob/master/human_eval/evaluation.py
"""
import threading
import time
import concurrent.futures

def fun(name):
	if name == "3":
		time.sleep(0.2)
	print(name)
	return name
    

if __name__ == "__main__":
	with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
		futures = []
		for i in range(20):
			future = executor.submit(fun, name=str(i))
			futures.append(future)

		results = []
		for future in concurrent.futures.as_completed(futures):
			result = future.result()
			results.append(result)

		print(results)