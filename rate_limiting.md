# Rate limiting

Google Cloud Apigee has 2 types of rate limiting policies:
* Quota
* SpikeArrest

Here are the main differences between the 2 policies:[^1][^2]

|          |Quota|SpikeArrest|
|----------|-----|-----------|
|Purpose|Limit the number of requests in a specific period of time to enforce business contracts or SLAs|Protect against severe traffic spikes including DDoS attacks|
|Level|user, organization, API endpoint, and/or API|API|
|Time|minutes to months|seconds to minutes|

There are 3 Quota policy types:[^3]
* **calendar**: We supply a start time, an interval (i.e., a number of time units) and a time unit (minute, hour, day, week or month). For example, the start time might be "2021-7-16 12:00:00", the interval might be 3 and the time unit might be days. In this case, the number of requests would be calculated between [2021-7-16 12:00:00, 2021-7-19 12:00:00] and then between [2021-7-19 12:00:00, 2021-7-22 12:00:00] and so on.
* **rollingwindow**: We supply an interval and a time unit. In this case, the number of requests would be calculated based on [time of the request - interval in time units, time of the request].
* **flexi**: Like calendar, except that the start time is not provided, but determined based on the time of the first request that comes in.

The calendar type is commonly used for billing purposes.

The rollingwindow type is used to limit requests over time without respect to a specific calendar period. For example, suppose a client sends a large number of requests just before the end of the calendar period and just after. The number of requests may fall below the rate limit in each calendar period, but together may amount to a large number of requests in a short period of time.

The rollingwindow type differs from the SpikeArrest policy in that the rollingwindow type can be applied more granularly than the SpikeArrest policy (specific users, organizations or endpoints rather than just to the API as a whole), but at a coarser level of time (minutes to months rather than seconds to minutes). These differences make the rollingwindow type suitable to distributing available load fairly across clients over time without respect to a specific calendar period rather than preventing severe spikes in traffic (including DDoS).

The flexi type is useful for trial periods.

As an example, OpenAI enforces rate limits "at the organization level, not user level, based on the specific endpoint used as well as the type of account you have" and those rate limits are "measured in two ways: RPM (requests per minute) and TPM (tokens per minute)."[^4]

For the SpikeArrest policy, we supply a per-second rate or a per-minute rate and a boolean UseEffectiveCount.[^5] If UseEffectiveCount is true, then burst in traffic are allowed as long as they do not exceed the given rate. Otherwise (the default), bursts in traffic are not allowed and traffic is smoothed over time.

Here are some different rate limiting algorithms in more detail.[^6]

In the **token bucket** algorithm, we add a token to the bucket at a fixed rate (e.g., if the given rate limit is 5 requests per second), then we add a token to the bucket every 1/5 seconds). The bucket has a fixed capacity. If we try to add a token to a bucket that is full, then that token is discarded. When a new request comes in, we check to see if the bucket has a token in it. If it does, then we take a token from the bucket and forward the request. Otherwise, we drop the request.

In the **leaky bucket** algorithm, we maintain a FIFO queue with a fixed capacity. When a new request comes in, we check to see if the queue is below capacity. If it is, then we add the request to the queue. Otherwise, we drop the request. We pull requests from the queue at a fixed rate.

In the **fixed window** algorithm, we divide time into windows of some fixed length and associate a counter with each window. When a new request comes in, we find the window of time that the request time falls into. If the counter associated with that window is below the rate limit, we increment the counter by one and forward the request. Otherwise, we drop the request.

In the **sliding window log** algorithm, we keep each request time in a sorted set or similar data structure. When a new request comes in, we remove request times older than (new request time - window size) and add the new request time. If the log size is below the rate limit, then we forward the request. Otherwise, we drop the request. Note that we store the request time even if the request is dropped.

In the **sliding window counter** algorithm, we divide time into windows of some fixed length and associate a counter with each window. When a new request comes in, we find the window of time that the request time falls into as well as the previous window. If the (previous window's counter * (1 - percentage into the current window) + current window's counter) is below the rate limit, we increment the counter by one and forward the request. Otherwise, we drop the request.

This [post](http://web.archive.org/web/20230424211714/https://redis.com/glossary/rate-limiting/) provides somes pseudocode to implement rate limiting in Redis using the INCR and EXPIRE commands.

## Footnotes

[^1]: http://web.archive.org/web/20230421165434/https://cloud.google.com/apigee/docs/api-platform/develop/comparing-quota-and-spike-arrest-policies
[^2]: http://web.archive.org/web/20230424154743/https://docs.apigee.com/api-platform/develop/comparing-quota-spike-arrest-and-concurrent-rate-limit-policies
[^3]: http://web.archive.org/web/20230424153437/https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy
[^4]: http://web.archive.org/web/20230421152715/https://platform.openai.com/docs/guides/rate-limits/overvie
[^5]: http://web.archive.org/web/20230424153606/https://cloud.google.com/apigee/docs/api-platform/reference/policies/spike-arrest-policy
[^6]: https://bytebytego.com/courses/system-design-interview/design-a-rate-limiter