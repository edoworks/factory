import costRouter from "../plugins/cost-router.mjs";


try {
  const hooks = await costRouter();
  await hooks.config({});
  process.stdout.write('{"routing_ready":true}\n');
} catch (error) {
  process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
  process.exitCode = 1;
}
