import logging
from google.protobuf.empty_pb2 import Empty
from hello_legacy_grpc.v1 import greeter_pb2, greeter_pb2_grpc
from hello_legacy_grpc.v1.greeter_rsm import (
    GetSalutationResponse,
    GreetRequest,
    GreetResponse,
    ResembleGreeter,
)
from resemble.aio.contexts import (
    Context,
    ReaderContext,
    WorkflowContext,
    WriterContext,
)

logging.basicConfig(level=logging.INFO)


class ResembleGreeterServicer(ResembleGreeter.Interface):

    async def _get_deprecated_salutation(self, context: Context) -> str:
        """Fetch a salutation from the deprecated Greeter service written in
        legacy gRPC."""
        # All legacy gRPC services hosted by Resemble can be reached via the
        # same channel.
        #
        # WARNING: Calls to legacy gRPC services will not get the same safety
        # guarantees as Resemble calls. Calls from Resemble state machines to
        # legacy services should be wrapped in Tasks if they represent
        # side-effects. See https://docs.reboot.dev/docs/model/side_effects.
        #
        # In this example, `DeprecatedGreeter`'s `GetSalutation` RPC
        # is a pure function, so it is safe to access from our context.
        async with context.legacy_grpc_channel() as channel:
            # Now that we have a channel for our legacy servicer, we can call
            # its gRPC methods in the standard gRPC fashion.
            deprecated_greeter_stub = greeter_pb2_grpc.DeprecatedGreeterStub(
                channel
            )

            salutation_response = await deprecated_greeter_stub.GetSalutation(
                Empty()
            )
            return salutation_response.salutation

    async def Greet(
        self,
        context: WriterContext,
        state: ResembleGreeter.State,
        request: GreetRequest,
    ) -> GreetResponse:
        salutation = await self._get_deprecated_salutation(context)
        state.num_greetings += 1

        pluralized_phrase = (
            "person has" if state.num_greetings == 1 else "people have"
        )
        return GreetResponse(
            message=f"{salutation}, {request.name}! "
            f"{state.num_greetings} {pluralized_phrase} been greeted today "
            f"by the Resemble service."
        )

    async def GetSalutation(
        self,
        context: ReaderContext,
        state: ResembleGreeter.State,
        request: Empty,
    ) -> GetSalutationResponse:
        # Imagine that this method is not yet implemented in this servicer!
        # It can call out to the deprecated gRPC servicer instead.
        salutation = await self._get_deprecated_salutation(context)
        return GetSalutationResponse(salutation=salutation)

    async def Initialize(
        self,
        context: WorkflowContext,
        request: Empty,
    ):
        # Call the ProxyGreeter service for a few greetings.
        #
        # NOTE: we don't currently have a way to call legacy gRPC
        # _idempotently_ (that's one of the reasons for Resemble!), so
        # for now we assume/hope that this workflow won't get retried
        # due to a failure but it's totally possible and if it happens
        # we might perform extra greets!
        async with context.legacy_grpc_channel() as channel:
            proxy_greeter_stub = greeter_pb2_grpc.ProxyGreeterStub(channel)

            for i in range(10):
                greet_response = await proxy_greeter_stub.Greet(
                    greeter_pb2.GreetRequest(name="legacy gRPC")
                )
                logging.info(
                    f"Received a greeting: '{greet_response.message}'"
                )

        return Empty()
