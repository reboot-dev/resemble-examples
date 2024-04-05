import unittest
from account_servicer import AccountServicer
from bank.v1.account_rsm import Account, BalanceResponse
from bank.v1.errors_pb2 import OverdraftError
from resemble.aio.tests import Resemble
from resemble.aio.workflows import Workflow
from unittest import mock


def report_error_to_user(error_message: str) -> None:
    # This is a dummy function for use in documentation code snippets.
    pass


class TestAccount(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.rsm = Resemble()
        await self.rsm.start()

    async def asyncTearDown(self) -> None:
        await self.rsm.stop()

    async def test_basics(self) -> None:
        workflow: Workflow = self.rsm.create_workflow(name=f"test-{self.id()}")

        await self.rsm.up(servicers=[AccountServicer])

        # Create the state machine by calling its constructor. The fact that the
        # state machine _has_ a constructor means that this step is required
        # before other methods can be called on it.
        account, _ = await Account.Open(
            "testing-account",
            workflow,
            customer_name="Alice",
        )

        # We can now call methods on the state machine. It should have a balance
        # of 0.
        response: BalanceResponse = await account.Balance(workflow)
        self.assertEqual(response.balance, 0)

        # When we deposit money, the balance should go up.
        await account.Deposit(workflow, amount=100)
        response = await account.Balance(workflow)
        self.assertEqual(response.balance, 100)

        # When we withdraw money, the balance should go down.
        await account.Withdraw(workflow, amount=60)
        response = await account.Balance(workflow)
        self.assertEqual(response.balance, 40)

        # When we withdraw too much money, we should get an error.
        # Use a helper function here to get a code snippet for use in docs.
        async def withdraw():
            try:
                await account.Withdraw(workflow, amount=65)
            except Account.WithdrawAborted as aborted:
                match aborted.error:
                    case OverdraftError(amount=amount):
                        report_error_to_user(
                            'Your withdrawal could not be processed due to '
                            'insufficient funds. Your account balance is less '
                            f'than the requested amount by {amount} dollars.'
                        )
                raise

        with self.assertRaises(Account.WithdrawAborted) as aborted:
            await withdraw()

        self.assertTrue(isinstance(aborted.exception.error, OverdraftError))
        self.assertEqual(aborted.exception.error.amount, 25)
        # ... and the balance shouldn't have changed.
        response = await account.Balance(workflow)
        self.assertEqual(response.balance, 40)

    @mock.patch("account_servicer.send_email")
    async def test_send_welcome_email(self, mock_send_email) -> None:
        await self.rsm.up(
            servicers=[AccountServicer],
            # Normally, `rsm.up()` runs the servicers in a separate process, to
            # ensure that accidental use of blocking functions (an easy mistake
            # to make) don't cause the test to lock up. However, in this test
            # we're using a mock, which must be in the same process as the test
            # or it won't work.
            #
            # We MUST therefore pass `in_process=True` for `@patch` to work.
            in_process=True,
        )
        workflow: Workflow = self.rsm.create_workflow(name=f"test-{self.id()}")

        # When we open an account, we expect the user to receive a welcome
        # email.
        account, open_response = await Account.Open(
            "testing-account",
            workflow,
            customer_name="Alice",
        )

        # Wait for the email task to run.
        await Account.WelcomeEmailTaskFuture(
            workflow,
            task_id=open_response.welcome_email_task_id,
        )
        # We can expect two attempts to send the email, because Resemble always
        # re-runs methods twice in development mode in order to validate that
        # calls are idempotent.
        self.assertEquals(mock_send_email.call_count, 2)
