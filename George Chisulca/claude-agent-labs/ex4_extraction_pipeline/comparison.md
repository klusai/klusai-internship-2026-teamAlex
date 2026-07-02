\# Batch vs Synchronous Extraction



The Message Batches API is 50% cheaper in token cost than synchronous requests.



The trade-off is latency. Running `extract.py` synchronously is better for one invoice or an interactive workflow because the result comes back quickly. The batch path can take longer, potentially up to around an hour, but it is better for bulk or overnight processing.



I would use synchronous extraction for a single invoice, debugging, or user-facing interactive work. I would use batch extraction for many invoices where lower cost and throughput matter more than immediate results.

