from temporalio import activity, workflow


@activity.defn
async def say_hello(name: str) -> str:
    return f"Hello {name} from Temporal!"


@workflow.defn
class HelloWorkflow:

    @workflow.run
    async def run(self, name: str) -> str:
        result = await workflow.execute_activity(
            say_hello,
            name,
            start_to_close_timeout=timedelta(seconds=10),
        )

        return result


from datetime import timedelta