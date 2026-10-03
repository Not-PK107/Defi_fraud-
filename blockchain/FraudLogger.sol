// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract FraudLogger {

    struct FraudAlert {
        address walletAddress;
        uint256 riskScore;
        string fraudCategory;
        uint256 timestamp;
        address reportedBy;
    }

    FraudAlert[] public fraudAlerts;

    event FraudAlertLogged(
        address indexed walletAddress,
        uint256 riskScore,
        string fraudCategory,
        uint256 timestamp,
        address indexed reportedBy
    );

    function logFraud(
        address _walletAddress,
        uint256 _riskScore,
        string memory _fraudCategory
    ) public {  

        require(_walletAddress != address(0), "Invalid wallet address");
        require(_riskScore <= 100, "Risk score must be 0-100");

        FraudAlert memory newAlert = FraudAlert({
            walletAddress: _walletAddress,
            riskScore: _riskScore,
            fraudCategory: _fraudCategory,
            timestamp: block.timestamp,
            reportedBy: msg.sender
        });

        fraudAlerts.push(newAlert);

        emit FraudAlertLogged(
            _walletAddress,
            _riskScore,
            _fraudCategory,
            block.timestamp,
            msg.sender
        );
    }

    function getFraudAlertCount() public view returns (uint256) {
        return fraudAlerts.length;
    }

    function getFraudAlert(uint256 _index)
        public
        view
        returns (
            address walletAddress,
            uint256 riskScore,
            string memory fraudCategory,
            uint256 timestamp,
            address reportedBy
        )
    {
        require(_index < fraudAlerts.length, "Invalid alert index");

        FraudAlert memory alert = fraudAlerts[_index];

        return (
            alert.walletAddress,
            alert.riskScore,
            alert.fraudCategory,
            alert.timestamp,
            alert.reportedBy
        );
    }
}