from orchestration.steps.contracts import Step
from orchestration.run_pipeline import RunContext


class SampleStep:
    name = "sample_step"

    def run(self, ctx: RunContext) -> int:
        print(f"[STEP] {self.name} executed for pipeline={ctx.pipeline_name}")
        return 0
